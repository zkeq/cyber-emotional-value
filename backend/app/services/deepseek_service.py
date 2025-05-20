import httpx
import asyncio
import json
import time
import threading
from queue import Queue
from concurrent.futures import ThreadPoolExecutor

from app.core.config import settings
from app.core.redis_client import redis_client

class DeepSeekService:
    """DeepSeek API服务，负责多线程请求和消息队列管理"""
    
    def __init__(self):
        """初始化服务"""
        self.base_url = settings.DEEPSEEK_BASE_URL
        self.api_key = settings.DEEPSEEK_API_KEY
        self.thread_count = 12  # 固定为12个线程
        self.executor = ThreadPoolExecutor(max_workers=self.thread_count)
        self.active_sessions = {}  # 存储活跃会话的线程控制标志
        
    async def generate_messages(self, emotion_type, session_id, min_length=5, max_length=15):
        """生成情绪价值消息并放入Redis队列
        
        Args:
            emotion_type: 用户请求的情绪类型
            session_id: 会话ID，用于标识Redis队列
            min_length: 最小字数
            max_length: 最大字数
        """
        # 队列名称
        queue_name = f"messages:{session_id}"
        
        # 清空可能存在的旧队列
        redis_client.clear_queue(queue_name)
        
        # 创建计数器
        token_counter = f"tokens:{session_id}"
        redis_client.increment_counter(token_counter, 0)  # 初始化为0
        
        # 创建会话控制标志
        self.active_sessions[session_id] = True
        
        # 如果没有配置API密钥，使用预设消息
        if not self.api_key:
            print(f"未配置DeepSeek API密钥，使用预设消息")
            # 启动一个线程循环发送预设消息
            threading.Thread(
                target=self._send_default_messages,
                args=(queue_name, token_counter, session_id, min_length, max_length),
                daemon=True
            ).start()
            return
        
        # 启动多个线程请求DeepSeek API
        for i in range(self.thread_count):
            self.executor.submit(
                self._request_deepseek_api,
                emotion_type,
                queue_name,
                token_counter,
                session_id,
                i,
                min_length,
                max_length
            )
    
    def stop_generation(self, session_id):
        """停止指定会话的消息生成
        
        Args:
            session_id: 会话ID
        """
        if session_id in self.active_sessions:
            self.active_sessions[session_id] = False
            print(f"已停止会话 {session_id} 的消息生成")
    
    def _send_default_messages(self, queue_name, token_counter, session_id, min_length, max_length):
        """发送预设消息到Redis队列
        
        Args:
            queue_name: Redis队列名称
            token_counter: Token计数器名称
            session_id: 会话ID
            min_length: 最小字数
            max_length: 最大字数
        """
        message_index = 0
        
        # 过滤符合长度要求的预设消息
        filtered_messages = [msg for msg in settings.DEFAULT_MESSAGES if min_length <= len(msg) <= max_length]
        
        # 如果没有符合要求的消息，使用原始列表
        if not filtered_messages:
            filtered_messages = settings.DEFAULT_MESSAGES
        
        while self.active_sessions.get(session_id, False):
            # 从预设消息中选择一条
            message = filtered_messages[message_index % len(filtered_messages)]
            message_index += 1
            
            # 计算token数并更新计数器
            message_tokens = len(message) // 2 + 1
            redis_client.increment_counter(token_counter, message_tokens)
            
            # 将消息放入Redis队列
            redis_client.push_message(queue_name, json.dumps({
                "content": message,
                "tokens": message_tokens
            }))
            
            # 控制生成速率，降低密度
            time.sleep(1.5 / settings.MESSAGES_PER_SECOND)
        
        print(f"预设消息生成线程已结束: {session_id}")
    
    def _request_deepseek_api(self, emotion_type, queue_name, token_counter, session_id, thread_id, min_length, max_length):
        """请求DeepSeek API生成情绪价值消息
        
        Args:
            emotion_type: 用户请求的情绪类型
            queue_name: Redis队列名称
            token_counter: Token计数器名称
            session_id: 会话ID
            thread_id: 线程ID，用于日志
            min_length: 最小字数
            max_length: 最大字数
        """
        # 创建HTTP客户端
        client = httpx.Client(timeout=30.0)
        
        # 构建请求头
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # 构建优化后的提示词，更有温度和人情味
        prompt = f"""请以朋友的口吻，生成一句能给人{emotion_type}情绪价值的暖心话语，要求：
1. 字数在{min_length}-{max_length}之间
2. 语气真诚温暖，像朋友间的鼓励
3. 表达自然流畅，有共情和理解
4. 不要使用标点符号
5. 直接输出内容，不要有任何前缀或解释
"""
        
        # 请求参数，提高温度使输出更有变化
        data = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.8,
            "max_tokens": 50
        }
        
        # 持续请求，直到会话结束
        while self.active_sessions.get(session_id, False):
            try:
                # 发送请求
                response = client.post(
                    f"{self.base_url}/v1/chat/completions",
                    headers=headers,
                    json=data
                )
                
                # 检查响应状态
                if response.status_code == 200:
                    result = response.json()
                    message = result["choices"][0]["message"]["content"].strip()
                    tokens = result.get("usage", {}).get("total_tokens", len(message) // 2 + 1)
                    
                    # 过滤不符合长度要求的消息
                    if min_length <= len(message) <= max_length:
                        # 更新token计数
                        redis_client.increment_counter(token_counter, tokens)
                        
                        # 将消息放入Redis队列
                        redis_client.push_message(queue_name, json.dumps({
                            "content": message,
                            "tokens": tokens
                        }))
                        
                        print(f"线程 {thread_id} 生成消息: {message}, tokens: {tokens}")
                    else:
                        print(f"线程 {thread_id} 生成的消息长度不符合要求: {message}")
                else:
                    print(f"线程 {thread_id} API请求失败: {response.status_code} {response.text}")
                    # 如果API请求失败，使用预设消息
                    filtered_messages = [msg for msg in settings.DEFAULT_MESSAGES if min_length <= len(msg) <= max_length]
                    if not filtered_messages:
                        filtered_messages = settings.DEFAULT_MESSAGES
                    
                    message_index = int(time.time()) % len(filtered_messages)
                    message = filtered_messages[message_index]
                    tokens = len(message) // 2 + 1
                    
                    # 更新token计数
                    redis_client.increment_counter(token_counter, tokens)
                    
                    # 将消息放入Redis队列
                    redis_client.push_message(queue_name, json.dumps({
                        "content": message,
                        "tokens": tokens
                    }))
            
            except Exception as e:
                print(f"线程 {thread_id} 发生异常: {str(e)}")
            
            # 控制请求频率，降低密度
            time.sleep(3)  # 每个线程每3秒请求一次，避免API限流和减少弹幕密度
        
        print(f"API请求线程 {thread_id} 已结束: {session_id}")

# 创建全局服务实例
deepseek_service = DeepSeekService()
