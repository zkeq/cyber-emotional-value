from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from api.websocket import router as websocket_router
from core.praise_generator import start_praise_generation_task
from core.redis_manager import get_redis_client
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Praise Website Backend",
    description="A backend service for generating and streaming praise messages",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual frontend origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(websocket_router)

@app.on_event("startup")
async def startup_event():
    """Initialize Redis connection and start background tasks"""
    logger.info("Starting Praise Website Backend...")
    
    # Test Redis connection
    redis_client = await get_redis_client()
    try:
        await redis_client.ping()
        logger.info("Redis connection established successfully")
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        raise e
    
    # Start praise generation background task
    asyncio.create_task(start_praise_generation_task())
    logger.info("Background praise generation task started")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Praise Website Backend...")
    # Close Redis connections if needed
    redis_client = await get_redis_client()
    await redis_client.close()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        redis_client = await get_redis_client()
        await redis_client.ping()
        return {"status": "ok", "redis": "connected"}
    except Exception as e:
        return {"status": "error", "redis": "disconnected", "error": str(e)}

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Praise Website Backend API", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
