import os

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

# -------------------------
# CONFIG
# -------------------------

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "prakriti_db")
COLLECTION_NAME = "results"

# -------------------------
# CONNECTION
# -------------------------

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]


def save_result(data):
    try:
        result = collection.insert_one(data)
        return str(result.inserted_id)
    except Exception as e:
        print("MongoDB Error:", e)
        return None
    