from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    mongodb_url: str = "mongodb://localhost:27017"
    database_name: str = "novelty3_db"
    novelty1_api_url: str = "http://localhost:8001"
    novelty2_api_url: str = "http://localhost:8002"
    app_name: str = "Novelty3 Explanation Module"
    debug: bool = True

    class Config:
        env_file = ".env"

settings = Settings()