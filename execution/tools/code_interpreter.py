"""Sandboxed Python code interpreter."""
from __future__ import annotations

import subprocess
import sys
import tempfile
import os
from typing import Dict

from ..tools.registry import register


@register("code_interpreter")
def run_code(code: str, timeout: int = 10) -> Dict[str, str]:
    """
    Execute Python code in a subprocess sandbox.

    Returns a dict with ``stdout``, ``stderr``, and ``exit_code``.
    Production: replace subprocess with E2B or a Docker container.
    """
    with tempfile.NamedTemporaryFile(
        suffix=".py", mode="w", delete=False, encoding="utf-8"
    ) as tmp:
        tmp.write(code)
        tmp_path = tmp.name

    try:
        result = subprocess.run(
            [sys.executable, tmp_path],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": str(result.returncode),
        }
    except subprocess.TimeoutExpired:
        return {"stdout": "", "stderr": "Execution timed out.", "exit_code": "124"}
    finally:
        os.unlink(tmp_path)
