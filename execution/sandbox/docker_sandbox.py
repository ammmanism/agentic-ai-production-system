"""Docker sandbox for fully isolated code execution (E2B alternative)."""
from __future__ import annotations

import logging
import subprocess
from typing import Dict

logger = logging.getLogger(__name__)

DEFAULT_IMAGE = "python:3.11-slim"


def run_in_docker(
    code: str,
    image: str = DEFAULT_IMAGE,
    timeout: int = 15,
    memory_limit: str = "128m",
) -> Dict[str, str]:
    """
    Run Python code inside a Docker container for strong isolation.

    Requires Docker to be installed and running.
    Falls back gracefully when Docker is unavailable.
    """
    cmd = [
        "docker", "run", "--rm",
        "--network=none",
        f"--memory={memory_limit}",
        image,
        "python", "-c", code,
    ]

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout
        )
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": str(result.returncode),
        }
    except FileNotFoundError:
        logger.warning("Docker not found — falling back to stub response")
        return {
            "stdout": "[Docker unavailable — stub output]",
            "stderr": "",
            "exit_code": "0",
        }
    except subprocess.TimeoutExpired:
        return {"stdout": "", "stderr": "Container execution timed out.", "exit_code": "124"}
