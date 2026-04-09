from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class LLMProvider(ABC):
    """
    Abstract Base Class for all LLM interactions. 
    Enforces a strict Interface so the agent can switch seamlessly 
    between OpenAI, Anthropic, or Local vLLM endpoints.
    """
    
    @abstractmethod
    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        self.api_key = api_key
        self.model_name = model_name

    @abstractmethod
    async def invoke(self, messages: List[Dict[str, str]], temperature: float = 0.0) -> str:
        """
        Executes a standard conversational turn.
        Messages must be formatted as: [{'role': 'user|assistant|system', 'content': '...'}]
        """
        pass

    @abstractmethod
    async def invoke_with_tools(self, messages: List[Dict[str, str]], tools: List[Dict[str, Any]], temperature: float = 0.0) -> Dict[str, Any]:
        """
        Executes a request enforcing the LLM to output according to a JSON tool schema.
        Returns the parsed tool call dictionary.
        """
        pass
