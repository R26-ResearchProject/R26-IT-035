from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class Rec:
    rec_id: str
    category: str
    title: str
    text: str
    tags: list[str]
    expert_weight: float
    safety_level: str
    advice_strength: str


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


def _mk(
    rec_id: str,
    category: str,
    title: str,
    text: str,
    tags: list[str],
    *,
    expert_weight: float,
    safety_level: str = "safe",
    advice_strength: str = "moderate",
) -> Rec:
    # Keep tags clean and stable (lowercase, underscore).
    tags_clean = []
    for t in tags:
        t2 = str(t).strip().lower().replace(" ", "_")
        if t2 and t2 not in tags_clean:
            tags_clean.append(t2)

    return Rec(
        rec_id=rec_id,
        category=category,
        title=title.strip(),
        text=text.strip(),
        tags=tags_clean,
        expert_weight=round(_clamp01(float(expert_weight)), 2),
        safety_level=safety_level,
        advice_strength=advice_strength,
    )


def build_recommendations(start_id: int = 51, count: int = 200) -> list[Rec]:
    """
    Generate a curated-style library of supportive recommendations.

    Notes:
    - Non-pharmacologic, general wellness / skincare / hygiene guidance.
    - Avoids dosing, diagnosis, and treatment claims.
    - Uses tags so mappings can be added later without exploding combinations.
    """
    conditions = [
        ("eczema", ["dryness", "itching", "barrier_repair", "trigger_avoidance"]),
        ("acne", ["oil_control", "inflammation", "comedones", "hygiene"]),
        ("psoriasis", ["scaling", "inflammation", "gentle_care", "routine"]),
        ("fungal_infection", ["hygiene", "moisture_control", "breathable_clothing"]),
        ("dry_skin", ["hydration", "barrier_repair", "gentle_cleansing"]),
        ("contact_dermatitis", ["irritant_avoidance", "barrier_repair", "patch_testing"]),
        ("seborrheic_dermatitis", ["scalp_care", "gentle_cleansing", "stress_support"]),
        ("urticaria", ["trigger_tracking", "cooling", "stress_support"]),
        ("rosacea_like_redness", ["heat_avoidance", "gentle_cleansing", "cooling"]),
        ("hyperpigmentation_support", ["sun_protection", "gentle_care", "routine"]),
    ]

    # Topic blocks are designed to be applicable across many conditions.
    diet_topics = [
        ("Hydration-first plate", "Prioritize water-rich foods and regular fluids; dehydration can worsen skin discomfort.", ["hydration", "routine"]),
        ("Balanced low-spike meals", "Choose balanced meals and reduce frequent high-sugar spikes to support overall skin stability.", ["balanced_meals", "glycemic_support"]),
        ("Gentle gut-friendly routine", "Keep meal timing consistent and include fiber-rich foods to support digestion-related skin flares.", ["routine", "digestion_support"]),
        ("Cooling foods when heat is high", "When redness/heat sensations are present, prefer mild cooling foods and avoid very spicy choices.", ["cooling", "heat_support"]),
        ("Reduce ultra-processed triggers", "Limit ultra-processed foods that often correlate with flare cycles; observe your personal triggers.", ["trigger_avoidance", "tracking"]),
        ("Healthy fats for barrier support", "Include moderate healthy fats (as tolerated) to support the skin barrier and dryness control.", ["barrier_repair", "nutrition"]),
        ("Mindful dairy check (individualized)", "If you suspect dairy aggravates your skin, trial a short, monitored reduction and track changes.", ["trigger_tracking", "individualized"]),
    ]

    lifestyle_topics = [
        ("Consistent sleep window", "Aim for a consistent sleep schedule; irregular sleep can worsen itch, stress, and inflammation.", ["sleep", "routine"]),
        ("Stress downshift practice", "Use a short daily stress-downshift (breathing, walk, journaling) to reduce flare triggers.", ["stress_support", "routine"]),
        ("Sweat management habit", "After heavy sweating, change into dry clothing and cleanse gently to reduce irritation and fungal risk.", ["hygiene", "moisture_control"]),
        ("Trigger journal", "Track stress, weather, products, and foods during flares to find repeatable triggers.", ["tracking", "trigger_tracking"]),
        ("Sun-smart routine", "Use shade, hats, and consistent sun protection habits to reduce redness and pigmentation worsening.", ["sun_protection", "routine"]),
        ("Friction reduction", "Reduce friction from tight clothing and rough fabrics; friction can amplify irritation and redness.", ["friction_reduction", "gentle_care"]),
        ("Humidity and ventilation", "Keep living spaces ventilated; humidity control can help reduce fungal and irritation triggers.", ["home_environment", "moisture_control"]),
    ]

    home_care_topics = [
        ("Gentle cleansing rule", "Cleanse with mild, fragrance-free products; avoid harsh scrubbing that damages the barrier.", ["gentle_cleansing", "barrier_repair"]),
        ("Moisturize strategically", "Moisturize soon after bathing to lock in water and support barrier recovery.", ["barrier_repair", "hydration"]),
        ("Short lukewarm showers", "Prefer short lukewarm showers over long hot ones to reduce dryness and irritation.", ["barrier_repair", "gentle_care"]),
        ("Patch-test new products", "Test new skincare on a small area before full use to reduce contact reactions.", ["patch_testing", "irritant_avoidance"]),
        ("Nail and scratch control", "Keep nails short and use distractions to reduce scratching that worsens barrier injury.", ["itching_control", "barrier_repair"]),
        ("Clean textiles routine", "Wash towels and pillowcases regularly; clean textiles can reduce irritation and recurrence cycles.", ["hygiene", "routine"]),
        ("Breathable fabric choice", "Use breathable fabrics and avoid prolonged dampness in folds to reduce fungal recurrence risk.", ["breathable_clothing", "moisture_control"]),
        ("Cool compress (brief)", "Use a brief cool compress for heat/itch sensations; avoid prolonged cold exposure.", ["cooling", "comfort_support"]),
    ]

    category_sources: list[tuple[str, list[tuple[str, str, list[str]]]]] = [
        ("diet", diet_topics),
        ("lifestyle", lifestyle_topics),
        ("home_care", home_care_topics),
    ]

    # Condition-specific modifiers: title/text fragments and tag boosts.
    condition_adapters = {
        "eczema": ("Eczema-friendly", "For dryness/itch flares, keep routines simple and barrier-protective.", ["eczema_support"]),
        "acne": ("Acne-support", "For acne-prone skin, emphasize gentle cleansing and avoid picking or harsh over-stripping.", ["acne_support"]),
        "psoriasis": ("Psoriasis-support", "For scaling plaques, be extra gentle and avoid aggressive scrubbing.", ["psoriasis_support"]),
        "fungal_infection": ("Fungal-support", "For fungal-prone areas, prioritize dryness, ventilation, and sweat control habits.", ["fungal_support"]),
        "dry_skin": ("Dry-skin support", "For chronic dryness, prioritize moisture retention and barrier repair habits.", ["dryness"]),
        "contact_dermatitis": ("Irritant-aware", "If product irritation is suspected, reduce product load and introduce changes one-by-one.", ["contact_dermatitis_support"]),
        "seborrheic_dermatitis": ("Scalp/flake support", "For flaking patterns, keep cleansing consistent and avoid heavy occlusive buildup.", ["seborrheic_support"]),
        "urticaria": ("Hives-support", "For hive-like flares, focus on trigger tracking and calming routines; seek care for severe reactions.", ["urticaria_support"]),
        "rosacea_like_redness": ("Redness-support", "For flushing/redness, avoid heat triggers and keep products gentle and fragrance-free.", ["redness_support"]),
        "hyperpigmentation_support": ("Tone-support", "For uneven tone, prioritize sun protection and gentle routines; avoid irritation that can worsen marks.", ["pigmentation_support"]),
    }

    # Weight profiles per category (roughly).
    category_weight = {"diet": 0.84, "lifestyle": 0.83, "home_care": 0.9}

    # Safety defaults by topic keywords.
    caution_tags = {"patch_testing", "individualized"}

    recs: list[Rec] = []
    rec_num = start_id

    # We generate a pool by crossing condition blocks with topic blocks,
    # then take the first `count` after deterministic ordering.
    for condition, cond_tags in conditions:
        prefix, cond_line, cond_boost_tags = condition_adapters[condition]

        for category, topics in category_sources:
            for base_title, base_text, base_tags in topics:
                title = f"{prefix}: {base_title}"
                text = f"{base_text} {cond_line}"

                tags = [condition] + cond_tags + cond_boost_tags + base_tags

                safety_level = "safe"
                advice_strength = "moderate"
                if any(t in caution_tags for t in tags):
                    safety_level = "caution"
                if "sun_protection" in tags or "barrier_repair" in tags or "hygiene" in tags:
                    advice_strength = "strong"

                recs.append(
                    _mk(
                        rec_id=f"R{rec_num:03d}",
                        category=category,
                        title=title,
                        text=text,
                        tags=tags,
                        expert_weight=category_weight[category],
                        safety_level=safety_level,
                        advice_strength=advice_strength,
                    )
                )
                rec_num += 1

    # De-duplicate by (title, text) just in case.
    seen = set()
    unique: list[Rec] = []
    for r in recs:
        key = (r.title, r.text)
        if key in seen:
            continue
        seen.add(key)
        unique.append(r)

    # Trim to requested count.
    return unique[:count]


def _as_dicts(items: Iterable[Rec]) -> list[dict]:
    return [
        {
            "rec_id": r.rec_id,
            "category": r.category,
            "title": r.title,
            "text": r.text,
            "tags": r.tags,
            "expert_weight": r.expert_weight,
            "safety_level": r.safety_level,
            "advice_strength": r.advice_strength,
        }
        for r in items
    ]


def write_json(path: Path, items: Iterable[Rec]) -> None:
    path.write_text(json.dumps(_as_dicts(items), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_csv(path: Path, items: Iterable[Rec]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["rec_id", "category", "title", "text", "tags", "expert_weight", "safety_level", "advice_strength"])
        for r in items:
            w.writerow(
                [
                    r.rec_id,
                    r.category,
                    r.title,
                    r.text,
                    "|".join(r.tags),
                    r.expert_weight,
                    r.safety_level,
                    r.advice_strength,
                ]
            )


def main() -> None:
    base_dir = Path(__file__).resolve().parent.parent
    out_dir = base_dir / "data"
    out_dir.mkdir(parents=True, exist_ok=True)

    items = build_recommendations(start_id=51, count=200)
    write_json(out_dir / "recommendations_extra_200.json", items)
    write_csv(out_dir / "recommendations_extra_200.csv", items)
    print(f"Wrote {len(items)} recommendations to {out_dir}")


if __name__ == "__main__":
    main()

