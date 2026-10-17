"""LLM fallback for follow-up questions the rule-based intent parser can't handle.

Only used when the deterministic router in followup_qa.py finds no match for
why-not / compare / what-if. The rule-based path stays the default for
everything it can answer, since it's free, instant, and fully grounded in the
engine's own scored data. This module exists for the long tail of open
content questions (e.g. "what do you mean by small amount of ghee?") that
have no structured answer to retrieve.

Grounding: the model is only given this profile's current recommendation
list (title/category/text) plus the safety note — never asked to invent
medical facts, dosages, or advice beyond that text. If no provider API key
is configured, or the call fails for any reason, this returns None so the
caller falls back to the existing static help message. The feature is
therefore fully optional and never blocks the rest of the app.

Supports two providers, picked by whichever key is present (OpenAI checked
first since it's the one currently configured for this deployment):
- OpenAI:    OPENAI_API_KEY      (default model: gpt-4o-mini — cheap tier)
- Anthropic: ANTHROPIC_API_KEY   (default model: claude-haiku-4-5)
Override the model for either with AI_FALLBACK_MODEL.
"""

import os
from typing import Any, Dict, List, Optional

DEFAULT_OPENAI_MODEL = "gpt-4o-mini"
DEFAULT_ANTHROPIC_MODEL = "claude-haiku-4-5-20251001"
MAX_TOKENS = 300

SYSTEM_PROMPT = (
    "You are a follow-up assistant embedded in an Ayurvedic Prakriti-aware skin-care "
    "recommendation app. You answer short follow-up questions about the recommendations "
    "already shown to the user in this session.\n\n"
    "Rules:\n"
    "- Answer ONLY using the recommendation context provided below. Do not invent "
    "quantities, ingredients, medical claims, or advice not present in that context.\n"
    "- If the context doesn't specify something (e.g. an exact dosage or quantity), say so "
    "plainly rather than guessing, and note it's general lifestyle guidance, not a medical "
    "instruction.\n"
    "- Keep answers under 80 words, plain language, no markdown headers.\n"
    "- If the question asks for medical diagnosis, treatment, or anything beyond the scope "
    "of this supportive guidance, recommend consulting a qualified dermatologist or "
    "Ayurvedic physician instead of answering directly.\n"
)


def is_configured() -> bool:
    """Whether an API key is present, without touching the network."""
    return bool(os.environ.get("OPENAI_API_KEY") or os.environ.get("ANTHROPIC_API_KEY"))


def generate_ai_answer(
    question: str,
    user_input: Dict[str, Any],
    analysis: Dict[str, Any],
) -> Optional[str]:
    """Ask the model to answer using only the current recommendation context.

    Returns None (never raises) if no key is configured or the call fails,
    so callers can transparently fall back to the rule-based help message.
    """
    if os.environ.get("OPENAI_API_KEY"):
        return _generate_openai(question, user_input, analysis)
    if os.environ.get("ANTHROPIC_API_KEY"):
        return _generate_anthropic(question, user_input, analysis)
    return None


def _generate_openai(
    question: str,
    user_input: Dict[str, Any],
    analysis: Dict[str, Any],
) -> Optional[str]:
    try:
        from openai import OpenAI  # imported lazily so the dependency is optional
    except ImportError:
        return None

    context = _build_context(user_input, analysis)

    try:
        client = OpenAI()
        response = client.chat.completions.create(
            model=os.environ.get("AI_FALLBACK_MODEL", DEFAULT_OPENAI_MODEL),
            max_tokens=MAX_TOKENS,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"{context}\n\nUser question: {question}"},
            ],
        )
        answer = (response.choices[0].message.content or "").strip()
        return answer or None
    except Exception:  # noqa: BLE001
        return None


def _generate_anthropic(
    question: str,
    user_input: Dict[str, Any],
    analysis: Dict[str, Any],
) -> Optional[str]:
    try:
        from anthropic import Anthropic  # imported lazily so the dependency is optional
    except ImportError:
        return None

    context = _build_context(user_input, analysis)

    try:
        client = Anthropic()
        response = client.messages.create(
            model=os.environ.get("AI_FALLBACK_MODEL", DEFAULT_ANTHROPIC_MODEL),
            max_tokens=MAX_TOKENS,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": f"{context}\n\nUser question: {question}"}],
        )
        text_blocks = [block.text for block in response.content if getattr(block, "type", None) == "text"]
        answer = "".join(text_blocks).strip()
        return answer or None
    except Exception:  # noqa: BLE001
        return None


def _build_context(user_input: Dict[str, Any], analysis: Dict[str, Any]) -> str:
    result = analysis.get("result", {})
    skin_result = user_input.get("skin_result", {})
    prakriti_result = user_input.get("prakriti_result", {})

    lines: List[str] = [
        f"Profile: {prakriti_result.get('dominant_prakriti', '-')}-dominant prakriti, "
        f"{skin_result.get('severity', '-')} {skin_result.get('predicted_condition', '-')}.",
        "",
        "Current recommendations shown to the user:",
    ]

    grouped = result.get("recommendations_by_category", {})
    for category, items in grouped.items():
        for item in items:
            lines.append(f"- [{category}] {item['title']}: {item['text']}")

    safety_note = result.get("safety_note")
    if safety_note:
        lines.append("")
        lines.append(f"Safety note shown to user: {safety_note}")

    return "\n".join(lines)
