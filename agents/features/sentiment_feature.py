from __future__ import annotations

from typing import Any, Dict

from agents.happiness_program_manager_agent import FeatureSpec, HappinessProgramManager


def can_handle(user_input: str, _context: Dict[str, Any]) -> bool:
    text = (user_input or "").lower()
    return "sentiment" in text or "polarity" in text or "tone score" in text


def _fallback_sentiment_score(text: str) -> float:
    positive_words = {"calm", "happy", "good", "joy", "grateful", "peaceful", "hope"}
    negative_words = {"sad", "angry", "stress", "anxious", "bad", "panic", "low"}
    lowered = (text or "").lower()
    pos = sum(word in lowered for word in positive_words)
    neg = sum(word in lowered for word in negative_words)
    if pos == neg == 0:
        return 0.0
    return round((pos - neg) / max(pos + neg, 1), 3)


def handle(user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
    analyzer = context.get("analyze_sentiment")
    target_text = context.get("text", user_input)

    if callable(analyzer):
        score = float(analyzer(target_text))
    else:
        score = _fallback_sentiment_score(target_text)

    return {"text": target_text, "sentiment_score": round(score, 3)}


def register(manager: HappinessProgramManager) -> None:
    manager.register_feature(
        FeatureSpec(
            feature_id="sentiment_analysis",
            description="Computes sentiment polarity for user text.",
            can_handle=can_handle,
            handle=handle,
            priority=30,
        )
    )

