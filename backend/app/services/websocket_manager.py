import asyncio
import json
import time
from typing import Dict, List

from fastapi import WebSocket

from app.core.config import settings
from app.core.redis_client import redis_client
from app.services.deepseek_service import deepseek_service

class WebSocketManager:
    """WebSocket连接管理器，负责处理WebSocket连接和消息分发"""
    
    def __init__(self):
        """初始化连接管理器"""
        self.active_connections: Dict[str, WebSocket] = {}
        self.tasks: Dict[str, asyncio.Task] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        """处理新的WebSocket连接
        
        Args:
            websocket: WebSocket连接对象
            session_id: 会话ID
        """
        await websocket.accept()
        self.active_connections[session_id] = websocket
    
    def disconnect(self, session_id: str):
        """处理WebSocket断开连接
        
        Args:
            session_id: 会话ID
        """
        if session_id in self.active_connections:
            del self.active_connections[session_id]
        
        # 取消相关任务
        if session_id in self.tasks and not self.tasks[session_id].done():
            self.tasks[session_id].cancel()
            del self.tasks[session_id]
        
        # 停止后端消息生成线程
        deepseek_service.stop_generation(session_id)
    
    async def start_message_stream(self, emotion_type: str, session_id: str, min_length: int = 5, max_length: int = 15):
        """启动消息流处理
        
        Args:
            emotion_type: 用户请求的情绪类型
            session_id: 会话ID
            min_length: 最小字数
            max_length: 最大字数
        """
        # 启动DeepSeek API请求和消息生成
        await deepseek_service.generate_messages(emotion_type, session_id, min_length, max_length)
        
        # 创建消息分发任务
        self.tasks[session_id] = asyncio.create_task(
            self._dispatch_messages(session_id)
        )
    
    async def _dispatch_messages(self, session_id: str):
        """从Redis队列获取消息并分发到WebSocket
        
        Args:
            session_id: 会话ID
        """
        # 队列名称
        queue_name = f"messages:{session_id}"
        token_counter = f"tokens:{session_id}"
        
        # 记录开始时间
        start_time = time.time()
        message_count = 0
        
        try:
            while session_id in self.active_connections:
                # 从Redis队列获取消息（非阻塞）
                message_json = redis_client.pop_message(queue_name)
                
                if message_json:
                    # 解析消息
                    message_data = json.loads(message_json)
                    content = message_data["content"]
                    tokens = message_data.get("tokens", 0)
                    
                    # 更新计数
                    message_count += 1
                    
                    # 计算会话时长
                    session_duration = time.time() - start_time
                    
                    # 获取总token数
                    total_tokens = redis_client.get_counter(token_counter)
                    
                    # 发送消息到WebSocket
                    await self.active_connections[session_id].send_json({
                        "type": "message",
                        "content": content,
                        "session_duration": round(session_duration, 2),
                        "token_count": total_tokens,
                        "message_count": message_count
                    })
                    
                    # 控制发送速率，降低密度
                    await asyncio.sleep(1.5 / settings.MESSAGES_PER_SECOND)
                else:
                    # 队列为空，等待一小段时间
                    await asyncio.sleep(0.1)
        
        except asyncio.CancelledError:
            print(f"消息分发任务已取消: {session_id}")
            # 确保停止后端消息生成
            deepseek_service.stop_generation(session_id)
        except Exception as e:
            print(f"消息分发发生异常: {session_id}, {str(e)}")
            # 确保停止后端消息生成
            deepseek_service.stop_generation(session_id)
        finally:
            # 记录会话结束
            end_time = time.time()
            session_duration = end_time - start_time
            total_tokens = redis_client.get_counter(token_counter)
            print(f"消息分发结束: {session_id}, 持续时间: {session_duration:.2f}秒, 消息数: {message_count}, Token数: {total_tokens}")
            # 确保停止后端消息生成
            deepseek_service.stop_generation(session_id)

# 创建全局WebSocket管理器实例
websocket_manager = WebSocketManager()
