from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Manages all application settings. It automatically reads from environment
    variables and a .env file.
    """
    
    # --- Application Metadata ---
    PROJECT_NAME: str = "Fake News Detection API"
    API_V1_STR: str = "/api/v1"

    # --- Database Configuration ---
    # The type hint (str) ensures the value is loaded as a string.
    MONGO_DETAILS: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "fakenews_detector"

    # --- External API Keys ---
    # These fields are required. If not found in the environment or .env file,
    # Pydantic will raise a validation error on startup.
    X_BEARER_TOKEN: str

    # Pydantic-settings model configuration
    model_config = SettingsConfigDict(
        # The name of the file to load environment variables from.
        env_file=".env",
        # The character encoding for the .env file.
        env_file_encoding='utf-8',
        # Allows extra fields in the .env file that are not defined in this model.
        extra='ignore'
    )

# Create a single, importable instance of the settings that will be used
# across the entire application.
settings = Settings()

print("Application settings loaded successfully.")