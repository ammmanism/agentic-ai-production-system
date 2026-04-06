"""Calculator tool — safe evaluation of mathematical expressions."""
from __future__ import annotations

import ast
import math
import operator
from typing import Union

from .registry import register

_SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

_SAFE_NAMES = {k: getattr(math, k) for k in dir(math) if not k.startswith("_")}
_SAFE_NAMES["abs"] = abs
_SAFE_NAMES["round"] = round


def _safe_eval(node: ast.AST) -> Union[int, float]:
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.BinOp):
        op = _SAFE_OPERATORS.get(type(node.op))
        if op is None:
            raise ValueError(f"Unsupported operator: {node.op}")
        return op(_safe_eval(node.left), _safe_eval(node.right))
    if isinstance(node, ast.UnaryOp):
        op = _SAFE_OPERATORS.get(type(node.op))
        if op is None:
            raise ValueError(f"Unsupported unary operator: {node.op}")
        return op(_safe_eval(node.operand))
    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            raise ValueError("Only simple function calls are allowed")
        func = _SAFE_NAMES.get(node.func.id)
        if func is None:
            raise ValueError(f"Function not allowed: {node.func.id}")
        args = [_safe_eval(a) for a in node.args]
        return func(*args)
    raise ValueError(f"Unsupported expression type: {type(node)}")


@register("calculator")
def calculate(expression: str) -> Union[int, float]:
    """Safely evaluate a mathematical expression string."""
    try:
        tree = ast.parse(expression, mode="eval")
        return _safe_eval(tree.body)
    except Exception as exc:
        raise ValueError(f"Invalid expression '{expression}': {exc}") from exc
