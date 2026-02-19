from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

from agents.happiness_program_manager_agent import FeatureSpec, HappinessProgramManager


def can_handle(user_input: str, _context: Dict[str, Any]) -> bool:
    text = (user_input or "").lower()
    return "report" in text or "weekly" in text or "joy index" in text or "summary" in text


def handle(_user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
    report_fn = context.get("generate_weekly_report")
    joy_index_fn = context.get("generate_weekly_joy_index")

    if callable(report_fn):
        report = report_fn()
        return {"report": report, "generated_at": datetime.utcnow().isoformat() + "Z"}

    if callable(joy_index_fn):
        joy_index_fn()
        return {
            "report": "Weekly Joy Index job executed.",
            "generated_at": datetime.utcnow().isoformat() + "Z",
        }

    return {
        "report": "No report function available in context.",
        "generated_at": datetime.utcnow().isoformat() + "Z",
    }


def register(manager: HappinessProgramManager) -> None:
    manager.register_feature(
        FeatureSpec(
            feature_id="reporting",
            description="Triggers weekly report or joy-index generation.",
            can_handle=can_handle,
            handle=handle,
            priority=40,
        )
    )

