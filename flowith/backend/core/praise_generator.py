import asyncio
import concurrent.futures
import json
import uuid
import time
import random
import logging
from typing import Dict, Any
from core.redis_manager import get_redis_client

logger = logging.getLogger(__name__)

# Predefined praise messages (5-15 characters in Chinese)
PRAISE_MESSAGES = [
    "你今天真棒！",
    "你的笑容很美",
    "你很有才华",
    "你做得很好",
    "你很优秀",
    "你真是太厉害了",
    "你的想法很棒",
    "你很有创意", 
    "你的努力有回报",
    "你是个宝藏",
    "你很有魅力",
    "你的品味真好",
    "你很聪明",
    "你很细心",
    "你很温柔",
    "你很幽默",
    "你很可爱",
    "你很善良",
    "你很棒",
    "你真厉害",
    "你好优秀啊",
    "你太棒了",
    "你很特别",
    "你很了不起",
    "你很给力",
    "你真是天才",
    "你的想法太赞了",
    "你做事很认真",
    "你很有责任心",
    "你很靠谱",
    "你真的很棒",
    "你让人佩服",
    "你很有想法",
    "你很有潜力",
    "你进步很大",
    "你很努力",
    "你很用心",
    "你很专业",
    "你很厉害呢",
    "你真是太好了"
]

def simulate_deepseek_api(config: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Simulate calling deepseek API to generate praise messages
    
    Args:
        config: Configuration for the API call (baseurl, api_key, etc.)
        
    Returns:
        Dict containing generated text and token count
    """
    # Simulate API call delay
    time.sleep(random.uniform(0.1, 0.5))
    
    # Randomly select a praise message
    text = random.choice(PRAISE_MESSAGES)
    
    # Simulate token consumption (5-15 tokens based on text length)
    tokens = random.randint(5, 15)
    
    logger.debug(f"Generated praise: {text}, tokens: {tokens}")
    
    return {
        "text": text,
        "tokens": tokens
    }

async def generate_single_praise_task(redis_client, config: Dict[str, Any] = None):
    """
    Single praise generation task that calls the simulated API and pushes to Redis
    """
    loop = asyncio.get_event_loop()
    
    try:
        # Run the API simulation in thread pool to avoid blocking
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            praise_data = await loop.run_in_executor(
                executor, 
                simulate_deepseek_api, 
                config
            )
            
        if praise_data:
            # Create message structure
            message = {
                "id": str(uuid.uuid4()),
                "text": praise_data["text"],
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "tokens": praise_data["tokens"]
            }
            
            # Push to Redis queue
            await redis_client.rpush("praise_queue", json.dumps(message))
            logger.debug(f"Pushed message to Redis: {message['text']}")
            
            return message
            
    except Exception as e:
        logger.error(f"Error in praise generation task: {e}")
        return None

async def run_praise_generators(num_generators: int = 10):
    """
    Run multiple praise generation tasks concurrently
    """
    redis_client = await get_redis_client()
    config = {
        "base_url": "https://api.deepseek.com",  # Placeholder
        "api_key": "Placeholder"  # Placeholder
    }
    
    while True:
        try:
            # Create tasks for concurrent generation
            tasks = [
                generate_single_praise_task(redis_client, config)
                for _ in range(num_generators)
            ]
            
            # Wait for all tasks to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Count successful generations
            successful = sum(1 for result in results if result and not isinstance(result, Exception))
            logger.info(f"Generated {successful}/{num_generators} praise messages")
            
            # Wait before next generation cycle (target: ~10 messages per second)
            # With 10 generators, wait 1 second between cycles
            await asyncio.sleep(1.0)
            
        except Exception as e:
            logger.error(f"Error in praise generation cycle: {e}")
            await asyncio.sleep(5.0)  # Wait longer on error

async def start_praise_generation_task():
    """
    Start the background praise generation task
    """
    logger.info("Starting background praise generation...")
    
    # Start the praise generation loop
    await run_praise_generators(num_generators=10)
