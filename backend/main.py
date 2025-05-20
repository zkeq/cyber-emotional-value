from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio
import json
import time
import uuid
from typing import Optional

from app.core.config import settings
from app.core.redis_client import redis_client
from app.services.websocket_manager import websocket_manager

# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该限制为特定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 根路由
@app.get("/")
async def root():
    return {
        "message": "欢迎使用夸夸网站API",
        "version": settings.APP_VERSION,
        "status": "运行中"
    }

# 健康检查
@app.get("/health")
async def health_check():
    redis_status = "正常" if redis_client.ping() else "异常"
    return {
        "status": "健康",
        "redis": redis_status,
        "timestamp": time.time()
    }

# WebSocket路由，支持自定义字数范围
@app.websocket("/ws/{emotion_type}")
async def websocket_endpoint(
    websocket: WebSocket, 
    emotion_type: str,
    min_length: Optional[int] = Query(5),
    max_length: Optional[int] = Query(15)
):
    # 验证字数范围参数
    min_length = max(1, min(30, min_length))  # 限制在1-30之间
    max_length = max(min_length, min(50, max_length))  # 确保max_length >= min_length且不超过50
    
    # 生成唯一的会话ID
    session_id = f"session:{uuid.uuid4()}"
    
    # 记录会话开始时间
    start_time = time.time()
    
    try:
        # 建立WebSocket连接
        await websocket_manager.connect(websocket, session_id)
        
        # 发送会话开始消息
        await websocket.send_json({
            "type": "session_start",
            "session_id": session_id,
            "emotion_type": emotion_type,
            "min_length": min_length,
            "max_length": max_length,
            "timestamp": start_time
        })
        
        # 启动消息流，传递字数范围参数
        await websocket_manager.start_message_stream(emotion_type, session_id, min_length, max_length)
        
        # 保持连接直到客户端断开
        while True:
            # 接收客户端消息（用于心跳检测或其他控制命令）
            data = await websocket.receive_text()
            
            # 处理客户端消息
            try:
                message = json.loads(data)
                if message.get("type") == "ping":
                    await websocket.send_json({"type": "pong", "timestamp": time.time()})
                elif message.get("type") == "update_params":
                    # 处理参数更新请求
                    new_min = message.get("min_length", min_length)
                    new_max = message.get("max_length", max_length)
                    
                    # 验证新参数
                    new_min = max(1, min(30, new_min))
                    new_max = max(new_min, min(50, new_max))
                    
                    # 停止当前生成
                    websocket_manager.disconnect(session_id)
                    
                    # 使用新参数重新启动
                    session_id = f"session:{uuid.uuid4()}"
                    await websocket_manager.connect(websocket, session_id)
                    await websocket_manager.start_message_stream(emotion_type, session_id, new_min, new_max)
                    
                    # 更新当前参数
                    min_length = new_min
                    max_length = new_max
            except:
                # 忽略无效消息
                pass
            
    except WebSocketDisconnect:
        # 处理WebSocket断开连接
        websocket_manager.disconnect(session_id)
        
        # 记录会话结束
        end_time = time.time()
        session_duration = end_time - start_time
        token_counter = f"tokens:{session_id}"
        total_tokens = redis_client.get_counter(token_counter)
        print(f"WebSocket连接断开: {session_id}, 持续时间: {session_duration:.2f}秒, Token数: {total_tokens}")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
