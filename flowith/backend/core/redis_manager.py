import redis.asyncio as redis
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Global Redis client instance
_redis_client: Optional[redis.Redis] = None

async def get_redis_client() -> redis.Redis:
    """
    Get or create Redis client instance
    """
    global _redis_client
    
    if _redis_client is None:
        try:
            _redis_client = redis.Redis(
                host='localhost',  # Change to your Redis host
                port=6379,         # Change to your Redis port
                db=0,
                decode_responses=False,  # We'll handle encoding manually
                socket_keepalive=True,
                socket_keepalive_options={},
                health_check_interval=30,
            )
            
            # Test connection
            await _redis_client.ping()
            logger.info("Redis client created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create Redis client: {e}")
            raise e
    
    return _redis_client

async def close_redis_client():
    """
    Close Redis client connection
    """
    global _redis_client
    
    if _redis_client:
        await _redis_client.close()
        _redis_client = None
        logger.info("Redis client closed")
