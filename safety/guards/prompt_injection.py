import re
from typing import Tuple

# Unified list of suspicious patterns for prompt injection
SUSPICIOUS_PATTERNS = [
    r"(?i)ignore (all )?previous instructions",
    r"(?i)system override",
    r"(?i)you are now (a )?different (assistant|AI|system)",
    r"(?i)you are now an AI",
    r"(?i)forget (your|the) (instructions|rules|constraints)",
    r"(?i)new (rule|instruction):",
    r"(?i)pretend (you are|to be)",
    r"(?i)do not follow (your|the) (old|previous) (instructions|rules)",
    r"(?i)role[ -]?play as",
    r"(?i)jailbreak",
    r"(?i)developer mode",
    r"(?i)system\s*:",
    r"<!--.*?-->",
    r"(?i)!\[.*?\]\(.*?\)", # Markdown image injection
    r"(?i)(?:[A-Za-z0-9+/]{4}){5,}(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?", # Base64 payloads
]

COMPILED_PATTERNS = [re.compile(p) for p in SUSPICIOUS_PATTERNS]

def detect_injection(text: str) -> Tuple[bool, str]:
    """
    Detect potential prompt injection in user input using patterns.
    Returns (is_flagged, reason)
    """
    for pattern in COMPILED_PATTERNS:
        if pattern.search(text):
            return True, f"Blocked pattern: {pattern.pattern}"
    return False, ""

class PromptInjectionGuard:
    def __init__(self):
        self.compiled = COMPILED_PATTERNS

    def scan(self, user_input: str) -> Tuple[bool, str]:
        """
        Returns (is_malicious, reason)
        """
        return detect_injection(user_input)

    async def guard(self, user_input: str) -> None:
        """Raise an exception if injection is detected."""
        malicious, reason = self.scan(user_input)
        if malicious:
            raise ValueError(f"Prompt injection blocked: {reason}")
