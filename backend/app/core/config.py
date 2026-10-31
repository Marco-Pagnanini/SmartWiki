from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings, read from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str
    APP_NAME: str = "Smart Wiki"
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]

    # AI agents: create the key at https://console.anthropic.com
    ANTHROPIC_API_KEY: str | None = None
    ANTHROPIC_MODEL: str = "claude-haiku-5-5"
    # How much the model reasons: low | medium | high | xhigh | max (lower = fewer tokens, lower cost)
    ANTHROPIC_EFFORT: str = "low"
    # MCP server used by the agents (runs in this same backend)
    MCP_URL: str = "http://localhost:8000/mcp"


settings = Settings()
