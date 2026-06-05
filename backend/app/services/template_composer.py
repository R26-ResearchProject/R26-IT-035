# template_composer.py
# PURPOSE: Fills explanation templates with values
# from the disease knowledge base dataset.
#
# All context information (pregnancy, age, allergies)
# is merged DIRECTLY into the three main explanations.
# No separate fields are created for context.
#
# THREE MAIN OUTPUTS:
# 1. western    → disease facts + allergy alert
# 2. ayurvedic  → classical knowledge + pregnancy/age notes
# 3. personalized → fuzzy-driven + age advice + pregnancy warning
# 4. prevention → dosha advice + age/pregnancy warnings

import json
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Load all templates once when module loads
# Templates are stored as strings with {slot} placeholders
with open(
    "app/data/templates/templates_knowledge.json"
) as f:
    TEMPLATES = json.load(f)

# Maps each dosha to its physical effect on skin
# Used to fill {effect} slot in personalized template
DOSHA_EFFECTS = {
    "vata": "dryness, irregularity and rough skin patterns",
    "pitta": "inflammation, heat and reactive skin conditions",
    "kapha": "moisture retention, congestion and slow healing"
}


def fill_western_template(
    disease_data: dict,
    user_context: dict = None
) -> str:
    """
    Generates Western medical explanation.

    Base content: disease facts from dataset
    (symptoms, causes, triggers, complications)

    Context additions merged in:
    - If user has known allergies that match disease
      triggers, an allergy alert is added at the end
    """
    try:
        # Get western section from dataset
        w = disease_data["western"]

        # Fill base western template with disease facts
        explanation = TEMPLATES["western"].format(
            disease=disease_data["name"],
            category=disease_data["category"],
            description=w["description"],
            symptoms=", ".join(w["symptoms"]),
            causes=", ".join(w["causes"]),
            triggers=", ".join(w["triggers"]),
            complications=", ".join(w["complications"])
        )

        # MERGE ALLERGY ALERT
        # Check if user allergies match disease triggers
        if user_context:
            known_allergies = user_context.get(
                "known_allergies", []
            )
            if known_allergies:
                # Get disease trigger names as plain text
                disease_triggers = [
                    t["factor"].replace("_", " ")
                    for t in disease_data.get(
                        "trigger_factors", []
                    )
                ]

                # Find which allergies match triggers
                matched = []
                for allergy in known_allergies:
                    for trigger in disease_triggers:
                        if allergy.lower() in trigger.lower():
                            matched.append(allergy)

                # Add alert only if matches found
                if matched:
                    explanation += (
                        f" Based on your known allergies "
                        f"({', '.join(matched)}), these "
                        f"may be particularly significant "
                        f"triggers for your condition."
                    )
                    logger.info(
                        f"Allergy alert merged: {matched}"
                    )

        return explanation

    except Exception as e:
        logger.error(f"Western template error: {e}")
        # Return safe fallback if template fails
        return (
            f"{disease_data['name']} is a skin condition. "
            f"Please consult a dermatologist."
        )


def fill_ayurvedic_template(
    disease_data: dict,
    user_context: dict = None
) -> str:
    """
    Generates Ayurvedic explanation.

    Base content: Sanskrit name + dosha mapping
    + classical text reference

    Context additions merged in:
    - Pregnancy: safe/unsafe Ayurvedic options added
    - Age (non-adult): age-specific Ayurvedic note added
    """
    try:
        # Get ayurvedic section from dataset
        a = disease_data["ayurvedic"]

        # Combine primary and secondary dosha names
        dosha_list = (
            f"{a['primary_dosha'].title()} and "
            f"{a['secondary_dosha'].title()}"
        )

        # Fill base ayurvedic template
        explanation = TEMPLATES["ayurvedic"].format(
            western_name=disease_data["name"],
            ayurveda_name=a["sanskrit_name"],
            ayurveda_meaning=a["ayurveda_meaning"],
            dosha_list=dosha_list,
            dosha_cause=a["dosha_cause"],
            classical_text=a["classical_text"]
        )

        # MERGE PREGNANCY AYURVEDIC NOTE
        if user_context:
            if user_context.get("pregnancy_status"):

                # Get pregnancy data from dataset
                # Falls back to default if not in dataset
                preg = disease_data.get(
                    "pregnancy_considerations", {}
                )
                ayur_safe = preg.get(
                    "ayurvedic_safe",
                    [
                        "gentle coconut oil application",
                        "cooling diet",
                        "gentle neem wash"
                    ]
                )
                ayur_unsafe = preg.get(
                    "ayurvedic_unsafe",
                    [
                        "strong detox herbs",
                        "Panchakarma procedures"
                    ]
                )

                # Add pregnancy note to ayurvedic explanation
                explanation += (
                    f" During pregnancy, safe Ayurvedic "
                    f"options include "
                    f"{', '.join(ayur_safe)}. "
                    f"Avoid {', '.join(ayur_unsafe)} "
                    f"without medical supervision."
                )
                logger.info(
                    "Pregnancy Ayurvedic note merged"
                )

            # MERGE AGE-SPECIFIC AYURVEDIC NOTE
            # Only for non-adult age groups
            age_group = user_context.get(
                "age_group", "adult"
            )
            if age_group != "adult":
                age_data = disease_data.get(
                    "age_considerations", {}
                ).get(age_group, {})
                ayurvedic_note = age_data.get(
                    "ayurvedic_note", ""
                )
                if ayurvedic_note:
                    explanation += f" {ayurvedic_note}"
                    logger.info(
                        f"Age Ayurvedic note merged: "
                        f"{age_group}"
                    )

        return explanation

    except Exception as e:
        logger.error(f"Ayurvedic template error: {e}")
        return (
            f"Ayurvedic classification not available "
            f"for {disease_data['name']}."
        )


def fill_personalized_template(
    disease_data: dict,
    fuzzy_emphasis: dict,
    user_context: dict = None
) -> str:
    """
    Generates personalized explanation.
    This is the CORE of Novelty 3 research contribution.

    Base content: Driven by fuzzy engine output
    - dominant dosha from fuzzy scores
    - comparison with disease typical profile

    Context additions merged in:
    - Age-specific advice appended
    - Pregnancy warning with safe options appended
    """
    try:
        # Get dominant dosha from fuzzy engine output
        dominant = max(
            fuzzy_emphasis, key=fuzzy_emphasis.get
        )

        # Get disease primary dosha from dataset
        disease_primary = (
            disease_data["ayurvedic"]["primary_dosha"]
        )

        # Compare to determine susceptibility level
        # If user dominant matches disease primary dosha
        # they are more susceptible
        if dominant == disease_primary:
            comparison = (
                "strong alignment with the typical "
                "Ayurvedic profile, indicating high "
                "susceptibility"
            )
        else:
            comparison = (
                "a unique constitutional influence that "
                "modifies how this condition manifests "
                "for you"
            )

        # Fill personalized template with fuzzy values
        explanation = TEMPLATES["personalized"].format(
            dominant_dosha=dominant.title(),
            effect=DOSHA_EFFECTS[dominant],
            comparison_result=comparison,
            disease=disease_data["name"]
        )

        # MERGE CONTEXT-SPECIFIC ADDITIONS
        if user_context:

            # MERGE AGE-SPECIFIC ADVICE
            age_group = user_context.get(
                "age_group", "adult"
            )
            if age_group != "adult":
                age_data = disease_data.get(
                    "age_considerations", {}
                ).get(age_group, {})
                special_advice = age_data.get(
                    "special_advice", ""
                )
                if special_advice:
                    explanation += f" {special_advice}"
                    logger.info(
                        f"Age advice merged: {age_group}"
                    )

            # MERGE PREGNANCY WARNING WITH SAFE OPTIONS
            if user_context.get("pregnancy_status"):
                preg = disease_data.get(
                    "pregnancy_considerations", {}
                )
                safe = preg.get(
                    "safe_treatments",
                    [
                        "gentle moisturization",
                        "avoiding known triggers",
                        "cool compress"
                    ]
                )
                explanation += (
                    f" As you are currently pregnant, "
                    f"safe options for you include "
                    f"{', '.join(safe)}. "
                    f"Please consult your doctor before "
                    f"starting any new treatment."
                )
                logger.info("Pregnancy note merged")

        return explanation

    except Exception as e:
        logger.error(f"Personalized template error: {e}")
        return "Personalized explanation not available."


def fill_prevention_template(
    disease_data: dict,
    dominant_dosha: str,
    user_context: dict = None
) -> str:
    """
    Generates prevention advice.

    Base content: Disease prevention steps
    + dosha-specific advice from dataset

    Context additions merged in:
    - Pregnancy: doctor consultation warning added
    - Elderly: medication interaction warning added
    - Child: pediatrician consultation added
    """
    try:
        # Get prevention list from dataset
        prevention = ", ".join(disease_data["prevention"])

        # Get dosha-specific advice from dataset
        # Different advice for Vata, Pitta, Kapha
        dosha_advice = (
            disease_data["dosha_advice"][dominant_dosha]
        )

        # Fill prevention template
        explanation = TEMPLATES["prevention"].format(
            disease=disease_data["name"],
            prevention=prevention,
            dominant_dosha=dominant_dosha.title(),
            dosha_advice=dosha_advice
        )

        # MERGE CONTEXT-SPECIFIC WARNINGS
        if user_context:

            # MERGE PREGNANCY WARNING
            if user_context.get("pregnancy_status"):
                preg = disease_data.get(
                    "pregnancy_considerations", {}
                )
                # Get specific pregnancy warning from dataset
                # Falls back to generic if not in dataset
                warning = preg.get(
                    "pregnancy_warning",
                    "Always consult your doctor "
                    "during pregnancy before starting "
                    "any new treatment."
                )
                explanation += f" {warning}"
                logger.info("Pregnancy prevention merged")

            # MERGE AGE-SPECIFIC WARNINGS
            age_group = user_context.get(
                "age_group", "adult"
            )

            if age_group == "elderly":
                # Elderly need medication interaction warning
                explanation += (
                    " As an older adult, check with "
                    "your doctor about any medication "
                    "interactions before starting "
                    "new treatments. Skin becomes more "
                    "sensitive with age."
                )
                logger.info("Elderly prevention merged")

            elif age_group == "child":
                # Children need pediatrician consultation
                explanation += (
                    " For children, always consult a "
                    "pediatrician before using any "
                    "medication or herbal treatment."
                )
                logger.info("Child prevention merged")

            elif age_group == "teenager":
                # Teenagers benefit from stress management
                explanation += (
                    " For teenagers, managing stress "
                    "from school and social activities "
                    "is especially important for "
                    "controlling flare-ups."
                )
                logger.info("Teenager prevention merged")

        return explanation

    except Exception as e:
        logger.error(f"Prevention template error: {e}")
        return (
            "Please consult a healthcare provider "
            "for prevention advice."
        )


def compose_full_explanation(
    disease_data: dict,
    fuzzy_emphasis: dict,
    user_context: dict = None
) -> dict:
    """
    MAIN FUNCTION.
    Composes complete dual explanation by calling
    all four template functions.

    All context (pregnancy, age, allergies) is
    merged directly into the main explanations.
    No separate fields created.

    Parameters:
    - disease_data: from MongoDB (your dataset)
    - fuzzy_emphasis: from fuzzy_engine.py
    - user_context: from Novelty 1/2 combined input

    Returns dict with all explanation parts ready
    to send to frontend.
    """

    # Get dominant dosha from fuzzy scores
    dominant = max(
        fuzzy_emphasis, key=fuzzy_emphasis.get
    )

    logger.info(
        f"Composing explanation for "
        f"{disease_data.get('name')} "
        f"dominant: {dominant} "
        f"context: {user_context}"
    )

    return {
        # Western with allergy alert merged if applicable
        "western": fill_western_template(
            disease_data,
            user_context
        ),

        # Ayurvedic with pregnancy + age notes merged
        "ayurvedic": fill_ayurvedic_template(
            disease_data,
            user_context
        ),

        # Personalized with age + pregnancy merged
        # This is the core fuzzy-driven output
        "personalized": fill_personalized_template(
            disease_data,
            fuzzy_emphasis,
            user_context
        ),

        # Prevention with age + pregnancy warnings merged
        "prevention": fill_prevention_template(
            disease_data,
            dominant,
            user_context
        ),

        # These are used by explanation_generator.py
        "dominant_dosha": dominant,
        "fuzzy_scores": fuzzy_emphasis
    }