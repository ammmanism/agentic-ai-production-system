import re
from typing import Tuple

INJECTION_PATTERNS = [
    r"ignore previous instructions",
    r"you are now (?:an|a) (?:AI|assistant) named",
    r"system:",
    r"<!--",
]

def detect_injection(text: str) -> Tuple[bool, str]:
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return True, pattern
    return False, ""
