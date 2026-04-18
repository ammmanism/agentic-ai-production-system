class AgenticError(Exception):
    """Base exception for all custom Agentic AI errors."""
    pass

class ConfigurationError(AgenticError):
    """Raised when environment variables or configurations are invalid."""
    pass

class PromptInjectionError(AgenticError):
    """Raised when a malicious prompt is detected at the boundary."""
    pass

class RetrievalError(AgenticError):
    """Raised when the vector-store or BM25 index fails to execute."""
    pass
