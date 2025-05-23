from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class PraiseMessage(BaseModel):
    """
    Pydantic model for praise messages
    """
    id: str = Field(..., description="Unique identifier for the message")
    text: str = Field(..., min_length=1, max_length=50, description="Praise text content")
    timestamp: str = Field(..., description="Message generation timestamp in ISO format")
    tokens: int = Field(..., ge=1, description="Number of tokens consumed for this message")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "text": "你今天真棒！",
                "timestamp": "2023-10-27T10:00:00Z",
                "tokens": 8
            }
        }

class PraiseResponse(BaseModel):
    """
    Response model for WebSocket messages containing praise
    """
    messages: list[PraiseMessage]
    
    class Config:
        schema_extra = {
            "example": {
                "messages": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "text": "你今天真棒！",
                        "timestamp": "2023-10-27T10:00:00Z",
                        "tokens": 8
                    }
                ]
            }
        }

class HealthResponse(BaseModel):
    """
    Health check response model
    """
    status: str
    redis: Optional[str] = None
    error: Optional[str] = None

class ConfigModel(BaseModel):
    """
    Configuration model for DeepSeek API simulation
    """
    base_url: str = Field(default="https://api.deepseek.com", description="Base URL for the API")
    api_key: str = Field(default="placeholder", description="API key for authentication")
    max_tokens: int = Field(default=15, ge=5, le=50, description="Maximum tokens per message")
    generation_interval: float = Field(default=1.0, ge=0.1, description="Interval between generation cycles")
