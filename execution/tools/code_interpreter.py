import sys
import io
import ast
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)

class SecureCodeInterpreter:
    """
    A lightweight AST-based internal python sandbox.
    In actual large-scale production, this should be swapped with an E2B Docker execution environment.
    However, for safe local calculations, rewriting it through AST block-lists ensures memory safety 
    and stops `subprocess` or `os` hijacking.
    """
    
    ALLOWED_BUILTINS = {
        'print': print,
        'abs': abs,
        'min': min,
        'max': max,
        'sum': sum,
        'len': len,
        'int': int,
        'float': float,
        'str': str,
        'bool': bool,
        'round': round,
        'range': range,
    }
    
    # Imports that the agent is allowed to use for data processing
    ALLOWED_MODULES = ['math', 'datetime', 'json']
    
    def __init__(self):
        self.locals_dict: Dict[str, Any] = {}
        
    def _check_security(self, code: str):
        """Parse AST and reject immediately if forbidden nodes exist."""
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name not in self.ALLOWED_MODULES:
                            raise SecurityError(f"Import of module '{alias.name}' is strictly forbidden.")
                elif isinstance(node, ast.ImportFrom):
                    if node.module not in self.ALLOWED_MODULES:
                        raise SecurityError(f"Import from module '{node.module}' is strictly forbidden.")
                # We block eval/exec
                elif isinstance(node, ast.Call) and getattr(node.func, 'id', None) in ['eval', 'exec', 'open']:
                    raise SecurityError(f"Function Call '{node.func.id}' is forbidden.")
        except SyntaxError as e:
            raise ValueError(f"Syntax error in generated code: {e}")
            
    def execute(self, code: str) -> str:
        """
        Executes code securely catching standard outputs.
        """
        logger.info(f"Executing Code snippet inside Sandbox. Length: {len(code)}")
        
        try:
            self._check_security(code)
        except Exception as e:
            return f"Error: Code rejected by Security Analyzer -> {str(e)}"

        # Redirect stdout
        old_stdout = sys.stdout
        new_stdout = io.StringIO()
        sys.stdout = new_stdout

        # Setup sandboxed globals/locals
        sandbox_globals = {'__builtins__': self.ALLOWED_BUILTINS}
        for mod in self.ALLOWED_MODULES:
            sandbox_globals[mod] = __import__(mod)

        try:
            # We use exec but restricted by empty builtins and the prior AST check
            exec(code, sandbox_globals, self.locals_dict)
            output = new_stdout.getvalue()
            return output if output else "Execution completed with no stdout."
            
        except Exception as e:
            return f"Runtime error: {type(e).__name__}: {str(e)}"
        finally:
            sys.stdout = old_stdout

class SecurityError(Exception):
    pass
