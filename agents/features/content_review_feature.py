from __future__ import annotations

from typing import Any, Dict, List

from agents.happiness_program_manager_agent import FeatureSpec, HappinessProgramManager


def can_handle(user_input: str, _context: Dict[str, Any]) -> bool:
    text = (user_input or "").lower()
    return "review" in text or "content" in text or "article" in text or "copy" in text


def _fallback_review(article: str) -> Dict[str, Any]:
    suggestions: List[str] = []
    if len(article.split()) > 180:
        suggestions.append("Shorten long sections for easier reading.")
    if "!" in article:
        suggestions.append("Reduce exclamation marks to keep tone gentle.")
    if any(word in article.lower() for word in ["must", "should", "always"]):
        suggestions.append("Soften directive language to avoid a preachy tone.")
    if not suggestions:
        suggestions.append("Content is clear; add one concrete grounding exercise.")

    return {
        "summary": "Basic content review completed.",
        "suggestions": suggestions,
    }


def handle(user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
    article = context.get("article", user_input)
    reviewer = context.get("review_content")

    if callable(reviewer):
        return {"review": reviewer(article)}

    return _fallback_review(article)


def register(manager: HappinessProgramManager) -> None:
    manager.register_feature(
        FeatureSpec(
            feature_id="content_review",
            description="Reviews content for emotional safety and clarity.",
            can_handle=can_handle,
            handle=handle,
            priority=20,
        )
    )

