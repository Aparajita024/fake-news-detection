from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Fake News Detection API"
    API_V1_STR: str = "/api/v1"
    MONGO_DETAILS: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "fakenews_detector"
    X_BEARER_TOKEN: str | None = None
    GEMINI_API_KEY: str | None  # optional in dev

    @property
    def is_gemini_configured(self) -> bool:
        return bool(self.GEMINI_API_KEY and self.GEMINI_API_KEY.startswith("sk-"))

    model_config = {
        "env_file": ".env",       # automatically loads from .env
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

settings = Settings()