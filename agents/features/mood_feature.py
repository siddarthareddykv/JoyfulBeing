from __future__ import annotations

from typing import Any, Dict

from agents.happiness_program_manager_agent import FeatureSpec, HappinessProgramManager


MOOD_KEYWORDS = {
    "mood",
    "feel",
    "feeling",
    "sad",
    "happy",
    "anxious",
    "stress",
    "worried",
    "angry",
}


def can_handle(user_input: str, _context: Dict[str, Any]) -> bool:
    text = (user_input or "").lower()
    excluded = ("sentiment", "polarity", "report", "summary", "review", "article", "content")
    if any(word in text for word in excluded):
        return False
    return any(word in text for word in MOOD_KEYWORDS)


def handle(user_input: str, context: Dict[str, Any]) -> str:
    ai_fn = context.get("generate_ai_guidance")
    local_fn = context.get("generate_local_guidance")

    if callable(ai_fn):
        try:
            return ai_fn(user_input)
        except Exception:
            pass

    if callable(local_fn):
        return local_fn(user_input)

    return (
        "Take one slow breath.\n"
        "Inhale for 4 counts, exhale for 6 counts for 2 minutes.\n"
        "Then do one small kind action for yourself today."
    )


def register(manager: HappinessProgramManager) -> None:
    manager.register_feature(
        FeatureSpec(
            feature_id="mood_guidance",
            description="Guides the user with calm mood support.",
            can_handle=can_handle,
            handle=handle,
            priority=10,
        )
    )
