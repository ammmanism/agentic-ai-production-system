"""Tool registry — central catalogue of available execution tools."""
from __future__ import annotations

from typing import Any, Callable, Dict, Optional

_REGISTRY: Dict[str, Callable[..., Any]] = {}


def register(name: str):
    """Decorator to register a tool function by name."""
    def decorator(fn: Callable[..., Any]):
        _REGISTRY[name] = fn
        return fn
    return decorator


def get_tool(name: str) -> Optional[Callable[..., Any]]:
    """Retrieve a registered tool by name. Returns None if not found."""
    return _REGISTRY.get(name)


def list_tools() -> Dict[str, Callable[..., Any]]:
    """Return a copy of the entire tool registry."""
    return dict(_REGISTRY)


def execute(name: str, **kwargs: Any) -> Any:
    """Execute a registered tool by name, passing keyword arguments."""
    tool = get_tool(name)
    if tool is None:
        raise ValueError(f"Unknown tool: '{name}'. Available: {list(_REGISTRY.keys())}")
    return tool(**kwargs)
