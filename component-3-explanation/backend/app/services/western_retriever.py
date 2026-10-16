# western_retriever.py
# Retrieves Western medical explanation for any disease.
# Uses three-tier strategy:
# Tier 1: Template based from dataset (no download needed)
# Tier 2: MedlinePlus API (thousands of diseases)
# Tier 3: Wikipedia API (almost everything)
# Tier 4: Fallback message (unknown diseases)
#
# NOTE: ChromaDB and sentence-transformers are disabled
# to avoid large model download during development.
# System uses MedlinePlus API as primary source.

import requests 
from app.utils.logger import get_logger

logger = get_logger(__name__)

# ChromaDB disabled — no model download needed
# Will be enabled after model downloads in future
model = None
western_collection = None

logger.info("Western retriever ready — using API mode")


def search_local_knowledge(disease_id: str) -> dict | None:
    """
    TIER 1: Local ChromaDB search.
    Currently disabled — returns None always.
    System falls through to MedlinePlus API.
    Will be enabled after ChromaDB model downloads.
    """
    # Disabled until model is downloaded
    return None


def fetch_from_medlineplus(disease_name: str) -> dict | None:
    """
    TIER 2: Fetch from MedlinePlus API.
    U.S. National Library of Medicine.
    Free, no API key needed.
    Covers thousands of diseases.

    Returns content dict if found, None if not found.
    """
    try:
        url = "https://connect.medlineplus.gov/service"
        params = {
            "mainSearchCriteria.v.dn": disease_name,
            "knowledgeResponseType": "application/json"
        }

        # Make API request with 10 second timeout
        response = requests.get(
            url, params=params, timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            entries = data.get("feed", {}).get("entry", [])

            if entries:
                # Get first result
                first = entries[0]
                summary = first.get(
                    "summary", {}
                ).get("_value", "")
                link = ""
                if first.get("link"):
                    link = first["link"][0].get("href", "")

                # Only return if summary has real content
                if summary and len(summary) > 50:
                    logger.info(
                        f"Tier 2 (MedlinePlus) found: {disease_name}"
                    )
                    return {
                        "explanation": summary,
                        "source": "MedlinePlus",
                        "source_detail": (
                            "U.S. National Library of Medicine"
                        ),
                        "source_url": link,
                        "quality": "medium",
                        "method": "medlineplus_api"
                    }

        return None

    except Exception as e:
        logger.error(f"MedlinePlus API error: {e}")
        return None


def fetch_from_wikipedia(disease_name: str) -> dict | None:
    """
    TIER 3: Fetch from Wikipedia Medical API.
    Covers almost every known medical condition.
    Used as fallback when MedlinePlus has no info.

    Returns content dict if found, None if not found.
    """
    try:
        # Format name for Wikipedia URL
        wiki_name = disease_name.replace(" ", "_")
        url = (
            f"https://en.wikipedia.org/api/rest_v1"
            f"/page/summary/{wiki_name}"
        )

        # Wikipedia requires User-Agent header
        headers = {
            "User-Agent": "Novelty3-ExplanationModule/1.0"
        }

        response = requests.get(
            url, headers=headers, timeout=10
        )

        if response.status_code == 200:
            data = response.json()

            # Only accept standard articles
            # Not disambiguation or missing pages
            if data.get("type") == "standard":
                extract = data.get("extract", "")
                page_url = (
                    data.get("content_urls", {})
                    .get("desktop", {})
                    .get("page", "")
                )

                if extract and len(extract) > 50:
                    logger.info(
                        f"Tier 3 (Wikipedia) found: {disease_name}"
                    )
                    return {
                        "explanation": extract,
                        "source": "Wikipedia Medical",
                        "source_detail": (
                            "Wikipedia — verify with a doctor"
                        ),
                        "source_url": page_url,
                        "quality": "medium",
                        "method": "wikipedia_api"
                    }

        return None

    except Exception as e:
        logger.error(f"Wikipedia API error: {e}")
        return None


def get_western_explanation(disease_id: str) -> dict:
    """
    Main function. Gets Western explanation for any disease.
    Tries each tier in order until one succeeds.

    Returns explanation dict always — never fails completely.
    """

    # Format disease name for API searches
    disease_name = disease_id.replace("_", " ")

    # TIER 1: Local ChromaDB (disabled for now)
    result = search_local_knowledge(disease_id)
    if result:
        return result

    # TIER 2: Try MedlinePlus API
    result = fetch_from_medlineplus(disease_name)
    if result:
        return result

    # TIER 3: Try Wikipedia API
    result = fetch_from_wikipedia(disease_name)
    if result:
        return result

    # TIER 4: Graceful fallback message
    # System never crashes — always returns something
    logger.warning(
        f"All tiers failed for: {disease_id}. Using fallback."
    )
    return {
        "explanation": (
            f"Detailed medical information for "
            f"{disease_name.title()} is not currently available "
            f"in our system. Please consult a qualified "
            f"dermatologist or visit DermNet NZ "
            f"(dermnetnz.org) or Mayo Clinic "
            f"(mayoclinic.org) for accurate information."
        ),
        "source": "System generated",
        "source_detail": "Please consult a medical professional",
        "quality": "low",
        "method": "fallback"
    }