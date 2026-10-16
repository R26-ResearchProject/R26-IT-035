# seed_database.py
# Loads disease and Prakriti datasets into MongoDB.
# Run this script ONCE after creating JSON files.
# Run again whenever you update the JSON files.
#
# Usage: python scripts/seed_database.py

import json
import sys
import os

# Add parent directory to path so imports work
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.services.mongodb_client import get_database
from app.utils.logger import get_logger

logger = get_logger(__name__)


def seed_diseases():
    """
    Loads disease_knowledge_dataset.json into MongoDB.
    Creates or updates one document per disease.
    """
    print("Loading diseases into MongoDB...")

    # Read JSON file
    with open(
        "app/data/datasets/disease_knowledge_dataset.json"
    ) as f:
        data = json.load(f)

    db = get_database()

    count = 0
    for disease in data["diseases"]:
        # Upsert = update if exists, insert if not
        db.diseases.update_one(
            {"disease_id": disease["disease_id"]},
            {"$set": disease},
            upsert=True
        )
        print(f"  Loaded: {disease['name']}")
        count += 1

    print(f"Diseases loaded: {count}")


def seed_prakriti():
    """
    Loads prakriti_knowledge_dataset.json into MongoDB.
    Creates or updates one document per Prakriti type.
    """
    print("\nLoading Prakriti traits into MongoDB...")

    # Read JSON file
    with open(
        "app/data/datasets/prakriti_knowledge_dataset.json"
    ) as f:
        data = json.load(f)

    db = get_database()

    count = 0
    for prakriti in data["prakriti_types"]:
        # Upsert = update if exists, insert if not
        db.prakriti_traits.update_one(
            {"prakriti_id": prakriti["prakriti_id"]},
            {"$set": prakriti},
            upsert=True
        )
        print(f"  Loaded: {prakriti['name']}")
        count += 1

    print(f"Prakriti types loaded: {count}")


if __name__ == "__main__":
    print("Starting database seeding...")
    print("Make sure MongoDB is running first.\n")

    try:
        seed_diseases()
        seed_prakriti()
        print("\nDatabase seeding complete.")
        print("You can now start the API server.")

    except Exception as e:
        print(f"\nError: {e}")
        print("Make sure MongoDB is running: mongod")