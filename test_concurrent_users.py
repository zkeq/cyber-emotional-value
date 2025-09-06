#!/usr/bin/env python3
"""
多用户并发测试脚本
用于测试夸夸网站后端的多用户并发支持能力
"""

import asyncio
import websockets
import json
import time
import uuid
import sys
from concurrent.futures import ThreadPoolExecutor

# 测试配置
BASE_URL = "ws://localhost:9096/ws"
CONCURRENT_USERS = 3  # 并发用户数
TEST_DURATION = 15  # 测试持续时间（秒）
EMOTION_TYPES = ["鼓励", "温暖", "治愈", "自信", "快乐"]

async def simulate_user(user_id):
    """模拟单个用户的WebSocket连接和消息接收
    
    Args:
        user_id: 用户ID，用于区分不同用户
    """
    emotion_type = EMOTION_TYPES[user_id % len(EMOTION_TYPES)]
    min_length = 5 + user_id  # 不同用户使用不同的字数范围
    max_length = 15 + user_id
    
    # 构建WebSocket URL
    ws_url = f"{BASE_URL}/{emotion_type}?min_length={min_length}&max_length={max_length}"
    
    print(f"用户 {user_id} 开始连接: {ws_url}")
    
    try:
        # 建立WebSocket连接
        async with websockets.connect(ws_url) as websocket:
            # 记录开始时间
            start_time = time.time()
            message_count = 0
            session_id = None
            
            # 设置接收超时
            while time.time() - start_time < TEST_DURATION:
                try:
                    # 接收消息（设置超时以避免无限等待）
                    message = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    data = json.loads(message)
                    
                    if data.get("type") == "session_start":
                        session_id = data.get("session_id")
                        print(f"用户 {user_id} 会话开始: {session_id}")
                    elif data.get("type") == "message":
                        message_count += 1
                        content = data.get("content", "")
                        # 每收到10条消息打印一次状态
                        if message_count % 10 == 0:
                            print(f"用户 {user_id} (会话 {session_id}) 已接收 {message_count} 条消息，最新: {content}")
                    
                    # 模拟用户交互，每5秒发送一次心跳
                    if message_count % 5 == 0:
                        await websocket.send(json.dumps({"type": "ping"}))
                
                except asyncio.TimeoutError:
                    # 超时不一定是错误，可能只是暂时没有消息
                    print(f"用户 {user_id} 等待消息超时")
                    continue
            
            # 测试结束
            elapsed = time.time() - start_time
            print(f"用户 {user_id} 测试完成: 持续 {elapsed:.2f} 秒，接收 {message_count} 条消息")
            
            # 发送一条消息通知服务器我们即将断开
            try:
                await websocket.send(json.dumps({"type": "bye"}))
            except:
                pass
    
    except Exception as e:
        print(f"用户 {user_id} 发生异常: {str(e)}")
    
    print(f"用户 {user_id} 连接已关闭")

async def run_concurrent_test():
    """运行并发用户测试"""
    print(f"开始并发测试: {CONCURRENT_USERS} 个用户, 持续 {TEST_DURATION} 秒")
    
    # 创建多个用户任务
    tasks = [simulate_user(i) for i in range(CONCURRENT_USERS)]
    
    # 并发运行所有用户任务
    await asyncio.gather(*tasks)
    
    print("并发测试完成")

if __name__ == "__main__":
    # 运行测试
    asyncio.run(run_concurrent_test())
