from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # API Settings
    APP_NAME: str = "Agentic AI Production System"
    API_V1_STR: str = "/api/v1"
    
    # Redis Settings
    REDIS_URL: str = "redis://localhost:6333"
    RATE_LIMIT_TOKENS: int = 100
    RATE_LIMIT_REFILL_RATE: float = 1.0
    
    # LLM Settings
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    VLLM_ENDPOINT: Optional[str] = None
    
    # RAG Settings
    QDRANT_URL: str = "http://localhost:6333"
    
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

settings = Settings()
