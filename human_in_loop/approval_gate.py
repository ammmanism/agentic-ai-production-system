"""Human-in-the-loop approval gate — pause execution until a human approves."""
from __future__ import annotations

import logging
import os
import time
import uuid
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

_POLL_INTERVAL = 2.0  # seconds between status checks
_DEFAULT_TIMEOUT = 300.0  # 5 minutes

# In-memory mock store: { "token": "pending" | "approved" | "rejected" }
_GLOBAL_APPROVAL_STORE: Dict[str, str] = {}


def approve_action(token: str) -> bool:
    if token in _GLOBAL_APPROVAL_STORE:
        _GLOBAL_APPROVAL_STORE[token] = "approved"
        return True
    return False


def reject_action(token: str) -> bool:
    if token in _GLOBAL_APPROVAL_STORE:
        _GLOBAL_APPROVAL_STORE[token] = "rejected"
        return True
    return False


class ApprovalGate:
    """
    Block agent execution until a human explicitly approves or rejects an action.

    In production: store pending approvals in Redis / DB with a unique token,
    expose a GET /approve/{token} endpoint, and have this class poll for the result.
    """

    def __init__(self, auto_approve_after: float = 0.0):
        self._auto_approve_after = auto_approve_after  # 0 = real blocking

    def request_approval(
        self,
        action: str,
        context: Optional[Dict[str, Any]] = None,
        timeout: float = _DEFAULT_TIMEOUT,
    ) -> bool:
        """
        Present an action to a human reviewer and block until decided.

        Returns True if approved, False if rejected or timed out.
        """
        token = str(uuid.uuid4())
        _GLOBAL_APPROVAL_STORE[token] = "pending"
        
        logger.info(
            "APPROVAL REQUIRED\nAction: %s\nContext: %s\nToken: %s",
            action,
            context or {},
            token
        )

        if self._auto_approve_after == 0.0:
            # Production: poll an external approval service (mocked here)
            deadline = time.monotonic() + timeout
            while time.monotonic() < deadline:
                status = _GLOBAL_APPROVAL_STORE.get(token)
                if status == "approved":
                    return True
                elif status == "rejected":
                    return False
                time.sleep(_POLL_INTERVAL)
            logger.warning("Approval timed out for action: %s", action)
            return False

        # Stub: auto-approve after a short delay
        logger.info("Auto-approving in %.1fs (test mode)", self._auto_approve_after)
        time.sleep(self._auto_approve_after)
        return True
