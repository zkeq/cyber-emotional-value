import httpx
import asyncio
import json
import time
import threading
import concurrent.futures
from queue import Queue
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

from app.core.config import settings
from app.core.redis_client import redis_client

class DeepSeekService:
    """DeepSeek API服务，负责多线程请求和消息队列管理"""
    
    def __init__(self):
        """初始化服务"""
        self.base_url = settings.DEEPSEEK_BASE_URL
        self.api_key = settings.DEEPSEEK_API_KEY
        self.thread_count_per_session = 12  # 每个会话的线程数
        self.active_sessions = {}  # 存储活跃会话的线程控制标志
        self.session_executors = {}  # 每个会话独立的线程池
        self.session_threads = {}  # 存储每个会话的线程列表
        self.lock = Lock()  # 用于保护共享资源的锁
        
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
        
        # 线程安全地设置会话控制标志
        with self.lock:
            self.active_sessions[session_id] = True
            
            # 如果已存在该会话的线程池，先关闭它
            if session_id in self.session_executors:
                self._cleanup_session_resources(session_id)
            
            # 为该会话创建新的线程池
            self.session_executors[session_id] = ThreadPoolExecutor(
                max_workers=self.thread_count_per_session,
                thread_name_prefix=f"session-{session_id}-"
            )
            self.session_threads[session_id] = []
        
        # 如果没有配置API密钥，使用预设消息
        if not self.api_key:
            print(f"未配置DeepSeek API密钥，使用预设消息")
            # 启动一个线程循环发送预设消息
            default_thread = threading.Thread(
                target=self._send_default_messages,
                args=(queue_name, token_counter, session_id, min_length, max_length),
                daemon=True,
                name=f"default-{session_id}"
            )
            default_thread.start()
            
            # 记录线程
            with self.lock:
                self.session_threads[session_id].append(default_thread)
            return
        
        # 启动多个线程请求DeepSeek API
        with self.lock:
            executor = self.session_executors.get(session_id)
            if executor:
                for i in range(self.thread_count_per_session):
                    future = executor.submit(
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
        with self.lock:
            if session_id in self.active_sessions:
                self.active_sessions[session_id] = False
                print(f"已停止会话 {session_id} 的消息生成")
                
                # 清理会话资源
                self._cleanup_session_resources(session_id)
    
    def _cleanup_session_resources(self, session_id):
        """清理会话相关的资源
        
        Args:
            session_id: 会话ID
        """
        # 必须在获取锁的情况下调用此方法
        if session_id in self.session_executors:
            try:
                # 尝试关闭线程池
                executor = self.session_executors[session_id]
                executor.shutdown(wait=False)
                del self.session_executors[session_id]
                print(f"已关闭会话 {session_id} 的线程池")
            except Exception as e:
                print(f"关闭会话 {session_id} 的线程池时发生异常: {str(e)}")
        
        # 移除会话线程记录
        if session_id in self.session_threads:
            del self.session_threads[session_id]
    
    def _send_default_messages(self, queue_name, token_counter, session_id, min_length, max_length):
        """发送预设消息到Redis队列
        
        Args:
            queue_name: Redis队列名称
            token_counter: Token计数器名称
            session_id: 会话ID
            min_length: 最小字数
            max_length: 最大字数
        """
        # 线程局部变量，确保独立性
        thread_queue_name = str(queue_name)
        thread_token_counter = str(token_counter)
        thread_session_id = str(session_id)
        thread_min_length = int(min_length)
        thread_max_length = int(max_length)
        
        message_index = 0
        
        print(f"[会话 {thread_session_id} 预设消息] 开始发送预设消息 ({thread_min_length}-{thread_max_length} 字)")
        
        # 过滤符合长度要求的预设消息
        filtered_messages = [msg for msg in settings.DEFAULT_MESSAGES if thread_min_length <= len(msg) <= thread_max_length]
        
        # 如果没有符合要求的消息，使用原始列表
        if not filtered_messages:
            filtered_messages = settings.DEFAULT_MESSAGES
            print(f"[会话 {thread_session_id} 预设消息] 警告: 没有符合长度要求的预设消息，使用全部消息")
        else:
            print(f"[会话 {thread_session_id} 预设消息] 找到 {len(filtered_messages)} 条符合要求的预设消息")
        
        # 安全地检查会话状态
        while True:
            is_active = False
            with self.lock:
                is_active = self.active_sessions.get(thread_session_id, False)
            
            if not is_active:
                print(f"[会话 {thread_session_id} 预设消息] 会话已停止，退出发送循环")
                break
                
            # 从预设消息中选择一条
            message = filtered_messages[message_index % len(filtered_messages)]
            message_index += 1
            
            # 计算token数并更新计数器
            message_tokens = len(message) // 2 + 1
            redis_client.increment_counter(thread_token_counter, message_tokens)
            
            # 将消息放入Redis队列
            redis_client.push_message(thread_queue_name, json.dumps({
                "content": message,
                "tokens": message_tokens
            }))
            
            print(f"[会话 {thread_session_id} 预设消息] 发送: {message} (tokens: {message_tokens})")
            
            # 控制生成速率，降低密度
            time.sleep(1.5 / settings.MESSAGES_PER_SECOND)
        
        print(f"[会话 {thread_session_id} 预设消息] 预设消息生成线程已结束")
    
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
        # 线程局部变量，确保每个线程都有独立的副本
        thread_emotion_type = str(emotion_type)
        thread_min_length = int(min_length)
        thread_max_length = int(max_length)
        thread_session_id = str(session_id)
        thread_queue_name = str(queue_name)
        thread_token_counter = str(token_counter)
        
        print(f"[会话 {thread_session_id} 线程 {thread_id}] 开始生成 '{thread_emotion_type}' 类型消息 ({thread_min_length}-{thread_max_length} 字)")
        
        # 创建HTTP客户端
        client = httpx.Client(timeout=30.0)
        
        # 构建请求头
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # 持续请求，直到会话结束
        while True:
            # 安全地检查会话状态
            is_active = False
            with self.lock:
                is_active = self.active_sessions.get(thread_session_id, False)
            
            if not is_active:
                print(f"[会话 {thread_session_id} 线程 {thread_id}] 会话已停止，退出生成循环")
                break
                
            try:
                # 在每次请求时重新构建提示词，确保使用当前线程的参数
                current_prompt = f"""请以朋友的口吻，生成一句能给人{thread_emotion_type}情绪价值的暖心话语，要求：
1. 字数在{thread_min_length}-{thread_max_length}之间
2. 语气真诚温暖，像朋友间的鼓励
3. 表达自然流畅，有共情和理解
4. 不要使用标点符号
5. 直接输出内容，不要有任何前缀或解释
"""
                
                # 每次请求都构建新的数据对象，避免引用共享
                request_data = {
                    "model": "deepseek-ai/DeepSeek-V3",
                    "messages": [{"role": "user", "content": current_prompt}],
                    "temperature": 0.8,
                    "max_tokens": 50
                }
                
                # 发送请求
                response = client.post(
                    f"{self.base_url}/v1/chat/completions",
                    headers=headers,
                    json=request_data
                )
                
                # 检查响应状态
                if response.status_code == 200:
                    result = response.json()
                    message = result["choices"][0]["message"]["content"].strip()
                    tokens = result.get("usage", {}).get("total_tokens", len(message) // 2 + 1)
                    
                    # 过滤不符合长度要求的消息
                    if thread_min_length <= len(message) <= thread_max_length:
                        # 更新token计数
                        redis_client.increment_counter(thread_token_counter, tokens)
                        
                        # 将消息放入Redis队列
                        redis_client.push_message(thread_queue_name, json.dumps({
                            "content": message,
                            "tokens": tokens
                        }))
                        
                        print(f"[会话 {thread_session_id} 线程 {thread_id}] 成功生成 '{thread_emotion_type}' 消息: {message} (tokens: {tokens})")
                        
                        ime.sleep(1)
                        # 成功生成消息后立即继续，不延迟
                        continue
                    else:
                        print(f"[会话 {thread_session_id} 线程 {thread_id}] 消息长度不符合要求 ({len(message)} 字): {message}")
                        # 长度不符合要求，短暂延迟后重试
                        time.sleep(0.5)
                else:
                    print(f"[会话 {thread_session_id} 线程 {thread_id}] API请求失败: {response.status_code} {response.text}")
                    # 如果API请求失败，使用预设消息
                    filtered_messages = [msg for msg in settings.DEFAULT_MESSAGES if thread_min_length <= len(msg) <= thread_max_length]
                    if not filtered_messages:
                        filtered_messages = settings.DEFAULT_MESSAGES
                    
                    # 使用线程ID和时间戳确保每个线程获取不同的消息
                    message_index = (int(time.time()) + thread_id) % len(filtered_messages)
                    message = filtered_messages[message_index]
                    tokens = len(message) // 2 + 1
                    
                    # 更新token计数
                    redis_client.increment_counter(thread_token_counter, tokens)
                    
                    # 将消息放入Redis队列
                    redis_client.push_message(thread_queue_name, json.dumps({
                        "content": message,
                        "tokens": tokens
                    }))
                    
                    print(f"[会话 {thread_session_id} 线程 {thread_id}] 使用预设消息 '{thread_emotion_type}': {message}")
                    
                    # API失败后短暂延迟再重试
                    time.sleep(1.0)
            
            except Exception as e:
                print(f"[会话 {thread_session_id} 线程 {thread_id}] 发生异常: {str(e)}")
                # 异常情况下延迟重试
                time.sleep(2.0)
        
        # 关闭HTTP客户端
        client.close()
        print(f"[会话 {thread_session_id} 线程 {thread_id}] '{thread_emotion_type}' 类型消息生成线程已结束")

# 创建全局服务实例
deepseek_service = DeepSeekService()
