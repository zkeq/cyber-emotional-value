import os
from dotenv import load_dotenv
from pydantic import BaseModel

# 加载环境变量
load_dotenv()

class Settings(BaseModel):
    """应用配置类"""
    # 应用信息
    APP_NAME: str = "夸夸网站API"
    APP_VERSION: str = "0.1.0"
    
    # Redis配置
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", "")
    
    # DeepSeek API配置
    DEEPSEEK_BASE_URL: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    
    # WebSocket配置
    WS_PING_INTERVAL: int = int(os.getenv("WS_PING_INTERVAL", "30"))
    
    # 应用配置
    THREAD_COUNT: int = int(os.getenv("THREAD_COUNT", "10"))
    MESSAGES_PER_SECOND: int = int(os.getenv("MESSAGES_PER_SECOND", "10"))
    
    # 预设的夸夸语句（当DeepSeek API未配置时使用）
    DEFAULT_MESSAGES: list = [
        "你真是太棒了！",
        "你的能力无人能及！",
        "你的思维太有创造力了！",
        "你的观点总是那么独特！",
        "你的笑容真的很治愈！",
        "你的坚持让人敬佩！",
        "你的细心令人感动！",
        "你的才华无人能及！",
        "你的努力终将得到回报！",
        "你的存在就是一种美好！",
        "你的眼光真是独到！",
        "你的成长速度惊人！",
        "你的气质无人能比！",
        "你的心态真的很阳光！",
        "你的潜力无限！",
        "你的魅力无人能挡！",
        "你的智慧令人折服！",
        "你的决断力太强了！",
        "你的温柔打动人心！",
        "你的勇气值得学习！"
    ]

# 创建全局设置对象
settings = Settings()
