"""Rule-based follow-up Q&A over a completed recommendation analysis.

Deliberately not an LLM: every answer is derived from data the engine already
computed (score components, exclusion reasons, or a re-run with a modified
context), so answers stay deterministic and explainable like the rest of the
module.
"""

import copy
import re
from typing import Any, Dict, List, Optional


DIETARY_PREFERENCES = {"vegetarian", "vegan", "lactose_intolerant", "lactose intolerant"}
CATEGORY_LABELS = {"diet": "Diet", "lifestyle": "Lifestyle", "home_care": "Home Care"}


def answer_question(
    question: str,
    user_input: Dict[str, Any],
    analysis: Dict[str, Any],
    engine: Any,
    top_k: int = 6,
) -> Dict[str, Any]:
    """Route a free-text question to the matching handler and return a reply payload."""
    normalized = question.strip().lower()
    if not normalized:
        return _reply("Ask me something like \"why not <recommendation title>\" or \"what if I'm vegan\".")

    what_if_target = _match_what_if(normalized)
    if what_if_target:
        return _answer_what_if(what_if_target, user_input, engine, top_k)

    why_not_target = _match_why_not(normalized)
    if why_not_target:
        return _answer_why_not(why_not_target, analysis)

    compare_targets = _match_compare(normalized)
    if compare_targets:
        return _answer_compare(compare_targets, analysis)

    ai_answer = _try_ai_fallback(question, user_input, analysis)
    if ai_answer:
        return _reply(ai_answer, source="ai")

    return _reply(
        "I can explain why a recommendation was or wasn't included, compare two "
        "recommendations, or re-run this profile under a different context. Try "
        "\"why not <title>\", \"why is X ranked above Y\", or \"what if I'm vegan\"."
    )


def _try_ai_fallback(question: str, user_input: Dict[str, Any], analysis: Dict[str, Any]) -> Optional[str]:
    """Best-effort AI fallback for questions the rule-based router can't classify."""
    try:
        from ai_fallback import generate_ai_answer
    except ImportError:
        return None
    return generate_ai_answer(question, user_input, analysis)


def _reply(text: str, **extra: Any) -> Dict[str, Any]:
    return {"answer": text, **extra}


def _match_why_not(text: str) -> Optional[str]:
    match = re.search(r"why (?:not|wasn'?t|isn'?t)\s+(.+?)(?:\s+recommended)?\??$", text)
    if match:
        return match.group(1).strip()
    return None


def _match_compare(text: str) -> Optional[List[str]]:
    match = re.search(r"why is\s+(.+?)\s+(?:ranked\s+)?above\s+(.+?)\??$", text)
    if match:
        return [match.group(1).strip(), match.group(2).strip()]
    return None


WHAT_IF_LEAD_IN = re.compile(
    r"what if i(?:'m| am| have| had|'ve| ve)\s+(.+?)\??$"
)
ALLERGIC_TO = re.compile(r"allerg(?:ic|y|ies)\s+to\s+([a-z0-9_ ]+)")
BARE_ALLERGY = re.compile(r"\ban?\s+allerg|\ballergies\b|\ballergic\b")


def _match_what_if(text: str) -> Optional[Dict[str, Any]]:
    match = WHAT_IF_LEAD_IN.search(text)
    if not match:
        return None
    clause = match.group(1).strip()

    allergen_match = ALLERGIC_TO.search(clause)
    if allergen_match:
        return {"type": "allergy", "value": allergen_match.group(1).strip()}

    if BARE_ALLERGY.search(clause):
        # "what if I have an allergy" with no substance named — can't act on
        # this without a specific tag, so ask a clarifying follow-up instead
        # of silently guessing or dumping the generic help text.
        return {"type": "allergy_clarify"}

    if clause in DIETARY_PREFERENCES or "vegan" in clause or "vegetarian" in clause or "lactose" in clause:
        pref = clause.replace(" ", "_")
        return {"type": "dietary_preference", "value": pref}

    if clause == "pregnant" or "pregnancy" in clause:
        return {"type": "pregnancy_status", "value": True}

    return {"type": "dietary_preference", "value": clause.replace(" ", "_")}


def _find_by_title_or_id(target: str, items: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    target_norm = target.strip().lower()
    for item in items:
        if item.get("rec_id", "").lower() == target_norm:
            return item
    for item in items:
        if item.get("title", "").lower() == target_norm:
            return item
    for item in items:
        if target_norm in item.get("title", "").lower():
            return item
    return None


def _answer_why_not(target: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
    exclusions = analysis.get("exclusions", [])
    all_scored = analysis.get("all_scored", [])
    selected_ids = set(analysis.get("selected_ids", []))

    excluded_match = _find_by_title_or_id(target, exclusions)
    if excluded_match:
        return _reply(
            f"\"{excluded_match['title']}\" ({excluded_match['rec_id']}) was excluded: "
            f"{excluded_match['reason']}"
        )

    scored_match = _find_by_title_or_id(target, all_scored)
    if scored_match:
        if scored_match["rec_id"] in selected_ids:
            return _reply(
                f"\"{scored_match['title']}\" ({scored_match['rec_id']}) is actually in the "
                f"current recommendation list, with score {scored_match['score']}."
            )
        return _reply(
            f"\"{scored_match['title']}\" ({scored_match['rec_id']}) scored {scored_match['score']} "
            f"but didn't make the top-K cut after ranking and category diversification — it wasn't "
            f"unsafe, just outranked by stronger matches."
        )

    return _reply(
        f"I couldn't find a recommendation matching \"{target}\" in this profile's candidate pool "
        f"(it may not apply to the current condition or prakriti at all)."
    )


def _answer_compare(targets: List[str], analysis: Dict[str, Any]) -> Dict[str, Any]:
    all_scored = analysis.get("all_scored", [])
    first = _find_by_title_or_id(targets[0], all_scored)
    second = _find_by_title_or_id(targets[1], all_scored)
    if not first or not second:
        missing = targets[0] if not first else targets[1]
        return _reply(f"I couldn't find a recommendation matching \"{missing}\" in this profile's candidate pool.")

    comps_a = first["score_components"]
    comps_b = second["score_components"]
    diffs = []
    for key in comps_a:
        delta = round(comps_a[key] - comps_b[key], 3)
        if abs(delta) >= 0.01:
            diffs.append(f"{key.replace('_', ' ')}: {comps_a[key]:.2f} vs {comps_b[key]:.2f}")

    diff_text = "; ".join(diffs) if diffs else "very similar component scores"
    return _reply(
        f"\"{first['title']}\" ({first['score']}) is ranked above \"{second['title']}\" "
        f"({second['score']}) mainly due to: {diff_text}."
    )


def _answer_what_if(change: Dict[str, Any], user_input: Dict[str, Any], engine: Any, top_k: int) -> Dict[str, Any]:
    if change["type"] == "allergy_clarify":
        current_tags = _all_candidate_tags(user_input, engine, top_k)
        example = next(iter(sorted(current_tags)), "pollen")
        return _reply(
            "Which allergen or ingredient are you concerned about? Try naming it, e.g. "
            f"\"what if I'm allergic to {example}\" — I'll re-check the current recommendations "
            "against that tag."
        )

    modified_input = copy.deepcopy(user_input)
    context = modified_input["user_context"]

    if change["type"] == "dietary_preference":
        context["dietary_preference"] = change["value"]
    elif change["type"] == "allergy":
        context.setdefault("known_allergies", [])
        if change["value"] not in [a.lower() for a in context["known_allergies"]]:
            context["known_allergies"].append(change["value"])
    elif change["type"] == "pregnancy_status":
        context["pregnancy_status"] = True

    new_analysis = engine.analyze(modified_input, top_k)
    new_result = new_analysis["result"]

    if new_analysis.get("blocked"):
        return _reply(
            "Under that change, recommendations would be blocked entirely: "
            f"{new_result.get('safety_note', 'safety policy triggered.')}"
        )

    original_by_id = {
        item["rec_id"]: {"title": item["title"], "category": category}
        for category, category_items in _current_selected(engine, user_input, top_k).items()
        for item in category_items
    }
    new_ids = {
        item["rec_id"]
        for category_items in new_result["recommendations_by_category"].values()
        for item in category_items
    }

    total = len(original_by_id)
    dropped_ids = [rec_id for rec_id in original_by_id if rec_id not in new_ids]
    kept = total - len(dropped_ids)

    if not dropped_ids:
        return _reply(
            f"Under that change, all {total} current recommendations would stay the same — "
            "none conflict with that condition."
        )

    dropped_lines = [
        f"{original_by_id[rec_id]['title']} ({CATEGORY_LABELS.get(original_by_id[rec_id]['category'], original_by_id[rec_id]['category'])})"
        for rec_id in dropped_ids
    ]
    return _reply(
        f"Under that change, {len(dropped_ids)} of your {total} current recommendations would be "
        f"dropped: {'; '.join(dropped_lines)}. The remaining {kept} would stay the same.",
        new_result=new_result,
    )


def _all_candidate_tags(user_input: Dict[str, Any], engine: Any, top_k: int) -> set:
    """Collect tags from this profile's current candidates to ground a clarifying example."""
    analysis = engine.analyze(user_input, top_k)
    tags = set()
    for item in analysis.get("all_scored", []):
        tags.update(tag.lower() for tag in item.get("tags", []))
    return tags


def _current_selected(engine: Any, user_input: Dict[str, Any], top_k: int) -> Dict[str, List[Dict[str, Any]]]:
    current = engine.analyze(user_input, top_k)["result"]
    return current["recommendations_by_category"]
