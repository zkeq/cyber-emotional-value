from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState
import json
import asyncio
import logging
from core.redis_manager import get_redis_client
from typing import List, Dict

logger = logging.getLogger(__name__)

router = APIRouter()

# Store active connections
active_connections: Dict[str, WebSocket] = {}

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        if websocket.client_state == WebSocketState.CONNECTED:
            await websocket.send_text(message)

manager = ConnectionManager()

@router.websocket("/ws/praise")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time praise message streaming
    """
    await manager.connect(websocket)
    
    # Start consuming messages from Redis and sending to this specific WebSocket
    consume_task = asyncio.create_task(
        consume_and_send_messages(websocket)
    )
    
    try:
        while True:
            # Keep the connection alive and handle any incoming messages
            try:
                # Wait for messages from client (optional - could be used for configuration)
                data = await asyncio.wait_for(websocket.receive_text(), timeout=1.0)
                logger.info(f"Received message from client: {data}")
                
                # Echo back or handle client message if needed
                response = {"type": "ack", "message": "Message received"}
                await websocket.send_json(response)
                
            except asyncio.TimeoutError:
                # No message received, continue listening
                continue
            except Exception as e:
                logger.error(f"Error receiving message: {e}")
                break
                
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected by client")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        # Cancel the consume task
        consume_task.cancel()
        manager.disconnect(websocket)

async def consume_and_send_messages(websocket: WebSocket):
    """
    Consume messages from Redis queue and send to WebSocket
    """
    redis_client = await get_redis_client()
    
    try:
        while websocket.client_state == WebSocketState.CONNECTED:
            try:
                # Block for a short time to get message from Redis queue
                result = await redis_client.blpop("praise_queue", timeout=1)
                
                if result:
                    # result is a tuple (key, value)
                    message_str = result[1].decode('utf-8')
                    
                    try:
                        message = json.loads(message_str)
                        # Send message to WebSocket client
                        await websocket.send_json([message])
                        logger.info(f"Sent message to client: {message['text']}")
                        
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to decode message from Redis: {e}")
                        continue
                        
                else:
                    # No message available, short delay to prevent busy waiting
                    await asyncio.sleep(0.1)
                    
            except asyncio.CancelledError:
                logger.info("Message consumption task cancelled")
                break
            except Exception as e:
                logger.error(f"Error consuming messages: {e}")
                await asyncio.sleep(1)  # Wait before retrying
                
    except Exception as e:
        logger.error(f"Fatal error in message consumption: {e}")
    finally:
        logger.info("Message consumption task ended")
