from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Impostazioni dell'applicazione, lette dalle variabili d'ambiente."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str
    APP_NAME: str = "Smart Wiki"
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]

    # Agenti AI: la chiave si crea su https://console.anthropic.com
    ANTHROPIC_API_KEY: str | None = None
    ANTHROPIC_MODEL: str = "claude-haiku-5-5"
    # Quanto ragiona il modello: low | medium | high | xhigh | max (più basso = meno token, meno costo)
    ANTHROPIC_EFFORT: str = "low"
    # Server MCP usato dagli agenti (gira nello stesso backend)
    MCP_URL: str = "http://localhost:8000/mcp"


settings = Settings()
