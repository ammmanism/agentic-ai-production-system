import os
import logging
from typing import List, Dict, Any, Optional
from .base import LLMProvider

try:
    from anthropic import AsyncAnthropic
except ImportError:
    AsyncAnthropic = None

logger = logging.getLogger(__name__)

class AnthropicProvider(LLMProvider):
    
    def __init__(self, api_key: Optional[str] = None, model_name: str = "claude-3-sonnet-20240229"):
        super().__init__(api_key, model_name)
        if AsyncAnthropic is None:
            raise ImportError("Please install the 'anthropic' package via pip.")
            
        key = self.api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not key:
            logger.warning("ANTHROPIC_API_KEY not found. Using dummy execution mode.")
            self.client = None
        else:
            self.client = AsyncAnthropic(api_key=key)

    async def invoke(self, messages: List[Dict[str, str]], temperature: float = 0.0) -> str:
        if not self.client:
            logger.debug(f"[Mock Anthropic] Received messages: {len(messages)}")
            return "This is a mock response from Anthropic Provider."
            
        logger.info(f"Invoking {self.model_name}")
        
        # Anthropic requires system prompt as a separate param
        system_msg = next((m["content"] for m in messages if m["role"] == "system"), None)
        user_msgs = [m for m in messages if m["role"] != "system"]
        
        response = await self.client.messages.create(
            model=self.model_name,
            max_tokens=4096,
            temperature=temperature,
            system=system_msg if system_msg else None,
            messages=user_msgs
        )
        return response.content[0].text

    async def invoke_with_tools(self, messages: List[Dict[str, str]], tools: List[Dict[str, Any]], temperature: float = 0.0) -> Dict[str, Any]:
        if not self.client:
            return {"name": "mock_tool", "arguments": {}}
            
        # Convert internal tool schema to Anthropic's tool spec
        raise NotImplementedError("Tool parsing schema mapper needed for Anthropic spec.")
