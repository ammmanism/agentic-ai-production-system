"""Active learner — use collected feedback to improve the system."""
from __future__ import annotations

import logging
from typing import Any, Dict, List

from .feedback_store import FeedbackStore

logger = logging.getLogger(__name__)

_MIN_RATING_FOR_POSITIVE = 4
_MAX_RATING_FOR_NEGATIVE = 2


class ActiveLearner:
    """
    Reads feedback signals and surfaces examples for fine-tuning / RLHF.

    Production workflow:
    1. Export high-confidence positive (rating >= 4) and negative (rating <= 2) examples.
    2. Format as DPO / PPO preference pairs.
    3. Submit to fine-tuning job (OpenAI Fine-Tunes API, Axolotl, etc.).
    """

    def __init__(self, feedback_store: FeedbackStore | None = None):
        self._store = feedback_store or FeedbackStore()

    def get_positive_examples(self) -> List[Dict[str, Any]]:
        """Return all feedback records with a positive rating."""
        return [
            r for r in self._store.load_all()
            if r.get("rating", 0) >= _MIN_RATING_FOR_POSITIVE
        ]

    def get_negative_examples(self) -> List[Dict[str, Any]]:
        """Return all feedback records with a negative rating."""
        return [
            r for r in self._store.load_all()
            if r.get("rating", 5) <= _MAX_RATING_FOR_NEGATIVE
        ]

    def export_preference_pairs(self) -> List[Dict[str, Any]]:
        """
        Build (chosen, rejected) preference pairs for DPO training.

        Returns a list of dicts with keys: session_id, chosen_rating, rejected_rating.
        In production: join with actual message content from your conversation store.
        """
        positives = self.get_positive_examples()
        negatives = self.get_negative_examples()

        pairs = []
        for pos in positives:
            for neg in negatives:
                if pos["session_id"] == neg["session_id"]:
                    pairs.append(
                        {
                            "session_id": pos["session_id"],
                            "chosen_message_id": pos["message_id"],
                            "rejected_message_id": neg["message_id"],
                            "chosen_rating": pos["rating"],
                            "rejected_rating": neg["rating"],
                        }
                    )
        logger.info("Exported %d preference pairs", len(pairs))
        return pairs
