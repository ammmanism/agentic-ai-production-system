from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator
from typing import Optional
from core.exceptions import ConfigurationError

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

    @model_validator(mode='after')
    def validate_api_keys(self) -> 'Settings':
        if not self.OPENAI_API_KEY and not self.ANTHROPIC_API_KEY and not self.VLLM_ENDPOINT:
            raise ConfigurationError("At least one LLM Provider must be configured (OpenAI, Anthropic, or vLLM).")
        return self

settings = Settings()
