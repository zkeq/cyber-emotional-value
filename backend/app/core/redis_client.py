import redis
from app.core.config import settings

class RedisClient:
    """Redis客户端类，用于管理Redis连接和操作"""
    
    def __init__(self):
        """初始化Redis连接"""
        self.connection = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
            decode_responses=True  # 自动将字节解码为字符串
        )
    
    def ping(self):
        """测试Redis连接"""
        return self.connection.ping()
    
    def push_message(self, queue_name, message):
        """向队列推送消息"""
        return self.connection.lpush(queue_name, message)
    
    def pop_message(self, queue_name, timeout=0):
        """从队列获取消息，支持阻塞操作"""
        if timeout > 0:
            # 阻塞式获取
            result = self.connection.brpop(queue_name, timeout)
            return result[1] if result else None
        else:
            # 非阻塞式获取
            return self.connection.rpop(queue_name)
    
    def get_queue_length(self, queue_name):
        """获取队列长度"""
        return self.connection.llen(queue_name)
    
    def clear_queue(self, queue_name):
        """清空队列"""
        return self.connection.delete(queue_name)
    
    def increment_counter(self, counter_name, amount=1):
        """增加计数器值"""
        return self.connection.incrby(counter_name, amount)
    
    def get_counter(self, counter_name):
        """获取计数器值"""
        value = self.connection.get(counter_name)
        return int(value) if value else 0

# 创建全局Redis客户端实例
redis_client = RedisClient()
