from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio
import json
import time

from app.core.config import settings
from app.core.redis_client import redis_client

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

# WebSocket路由
@app.websocket("/ws/{emotion_type}")
async def websocket_endpoint(websocket: WebSocket, emotion_type: str):
    await websocket.accept()
    
    # 生成唯一的会话ID
    session_id = f"session:{int(time.time())}"
    
    # 记录会话开始时间
    start_time = time.time()
    
    # 初始化计数器
    token_count = 0
    message_count = 0
    
    try:
        # 发送会话开始消息
        await websocket.send_json({
            "type": "session_start",
            "session_id": session_id,
            "emotion_type": emotion_type,
            "timestamp": start_time
        })
        
        # TODO: 这里将实现多线程DeepSeek API请求和Redis队列处理
        # 目前使用预设消息进行测试
        
        # 模拟消息发送
        while True:
            # 计算会话时长
            session_duration = time.time() - start_time
            
            # 从预设消息中选择一条
            message_index = message_count % len(settings.DEFAULT_MESSAGES)
            message = settings.DEFAULT_MESSAGES[message_index]
            
            # 模拟token消耗
            message_tokens = len(message) // 2 + 1
            token_count += message_tokens
            message_count += 1
            
            # 发送消息
            await websocket.send_json({
                "type": "message",
                "content": message,
                "session_duration": round(session_duration, 2),
                "token_count": token_count,
                "message_count": message_count
            })
            
            # 控制消息发送速率
            await asyncio.sleep(1 / settings.MESSAGES_PER_SECOND)
            
    except WebSocketDisconnect:
        # 记录会话结束
        end_time = time.time()
        session_duration = end_time - start_time
        print(f"WebSocket连接断开: {session_id}, 持续时间: {session_duration:.2f}秒, 消息数: {message_count}, Token数: {token_count}")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
