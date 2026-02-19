from __future__ import annotations

from typing import Optional


def build_review_prompt(article: str) -> str:
    return f"""
Review this content for:
- Emotional softness
- Simplicity
- Non-preachy tone
- Psychological grounding

Return:
1) One-line summary
2) 3 actionable improvements

Content:
{article}
""".strip()


def review_content(article: str, llm_client: Optional[object] = None, model: str = "gpt-4o-mini") -> str:
    if llm_client is None:
        raise ValueError("llm_client is required for dynamic content review.")

    prompt = build_review_prompt(article)
    response = llm_client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a concise wellness content reviewer."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=220,
        temperature=0.3,
    )
    return (response.choices[0].message.content or "").strip()

