from typing import List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class Message(BaseModel):
    role: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class AgentState(BaseModel):
    """Tracks the conversational state and reasoning history of an agent."""
    session_id: str
    history: List[Message] = Field(default_factory=list)
    context_window: int = 10
    
    def add_message(self, role: str, content: str, **metadata):
        self.history.append(Message(role=role, content=content, metadata=metadata))
        if len(self.history) > self.context_window * 2:
            # Simple truncation, could be replaced with summarization
            self.history = self.history[-self.context_window * 2:]

    def get_full_history(self) -> List[Dict[str, str]]:
        return [{"role": m.role, "content": m.content} for m in self.history]
