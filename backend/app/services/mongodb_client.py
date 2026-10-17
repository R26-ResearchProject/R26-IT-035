# mongodb_client.py
# Handles MongoDB Atlas cloud connection
# Uses SSL configuration for secure connection

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from app.config import settings
from app.utils.logger import get_logger
import ssl

logger = get_logger(__name__)

# Global variables to hold connection
client = None
database = None


def get_database():
    """
    Returns MongoDB database instance.
    Creates Atlas cloud connection on first call.
    Reuses existing connection on subsequent calls.
    """
    global client, database

    if database is None:
        try:
            # Connect to MongoDB Atlas with SSL settings
            client = MongoClient(
                settings.mongodb_url,
                serverSelectionTimeoutMS=30000,
                connectTimeoutMS=30000,
                socketTimeoutMS=30000,
                tls=True,
                tlsAllowInvalidCertificates=True
            )

            # Test connection is working
            client.admin.command("ping")

            # Get our specific database
            database = client[settings.database_name]

            logger.info(
                f"Connected to MongoDB Atlas: "
                f"{settings.database_name}"
            )

        except ConnectionFailure as e:
            logger.error(f"MongoDB connection failed: {e}")
            raise Exception(
                "Cannot connect to MongoDB. "
                "Check your Atlas connection string."
            )

    return database


def close_connection():
    """
    Closes the MongoDB Atlas connection.
    Called when application shuts down.
    """
    global client, database
    if client:
        client.close()
        client = None
        database = None
        logger.info("MongoDB Atlas connection closed")