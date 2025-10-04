from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Fake News Detection API"
    API_V1_STR: str = "/api/v1"
    MONGO_DETAILS: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "fakenews_detector"
    # Made optional so the app can start even if a token isn't provided during development
    X_BEARER_TOKEN: str | None = None

    # pydantic v2 / pydantic-settings configuration
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


settings = Settings()
print("Application settings loaded successfully.")