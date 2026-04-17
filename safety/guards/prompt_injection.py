import re
from typing import Tuple

class PromptInjectionGuard:
    def __init__(self):
        # Patterns that indicate possible prompt injection
        self.suspicious_patterns = [
            r"(?i)ignore all previous instructions",
            r"(?i)system override",
            r"(?i)you are now (a )?different (assistant|AI|system)",
            r"(?i)forget (your|the) (instructions|rules|constraints)",
            r"(?i)new (rule|instruction):",
            r"(?i)pretend (you are|to be)",
            r"(?i)do not follow (your|the) (old|previous) (instructions|rules)",
            r"(?i)role[ -]?play as",
            r"(?i)jailbreak",
            r"(?i)developer mode",
        ]
        self.compiled = [re.compile(p) for p in self.suspicious_patterns]

    def scan(self, user_input: str) -> Tuple[bool, str]:
        """
        Returns (is_malicious, reason)
        """
        for pattern in self.compiled:
            if pattern.search(user_input):
                return True, f"Detected pattern: {pattern.pattern}"
        return False, ""

    async def guard(self, user_input: str) -> None:
        """Raise an exception if injection is detected."""
        malicious, reason = self.scan(user_input)
        if malicious:
            raise ValueError(f"Prompt injection blocked: {reason}")
