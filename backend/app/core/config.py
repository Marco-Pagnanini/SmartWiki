from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Impostazioni dell'applicazione, lette dalle variabili d'ambiente."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str
    APP_NAME: str = "Smart Wiki"
    # In .env va scritta come lista JSON, es. ["http://localhost:5173"]
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]


settings = Settings()
