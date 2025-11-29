# app/config.py

try:
    # pydantic v2 moved BaseSettings into a separate package
    from pydantic_settings import BaseSettings
except Exception as exc:  # pragma: no cover - clear runtime error for missing package
    raise RuntimeError(
        "pydantic-settings is required (BaseSettings).\n"
        "Install it with: pip install pydantic-settings"
    ) from exc


class Settings(BaseSettings):
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database (optional helpers)
    DATABASE_URL: str | None = None
    DB_USER: str | None = None
    DB_PASS: str | None = None
    DB_HOST: str | None = None
    DB_PORT: str | None = None
    DB_NAME: str | None = None

    class Config:
        env_file = ".env"


settings = Settings()
