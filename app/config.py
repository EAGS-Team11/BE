# app/config.py

try:
    from pydantic_settings import BaseSettings
except Exception as exc:
    raise RuntimeError(
        "pydantic-settings is required (BaseSettings).\n"
        "Install it with: pip install pydantic-settings"
    ) from exc


class Settings(BaseSettings):
    # Security/Auth Settings
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

    # --- TAMBAHAN WAJIB (INI YANG MENYEBABKAN ERROR SEBELUMNYA) ---
    GEMINI_API_KEY: str | None = None 
    # -------------------------------------------------------------
    
    # Cloudinary (Opsional, tambahkan jika Anda menggunakannya di .env)
    CLOUDINARY_CLOUD_NAME: str | None = None
    CLOUDINARY_API_KEY: str | None = None
    CLOUDINARY_API_SECRET: str | None = None

    class Config:
        env_file = ".env"
        # Tambahan ini penting: agar jika ada variabel lain di .env yang tidak dipakai,
        # aplikasi TIDAK error (diabaikan saja)
        extra = "ignore" 


settings = Settings()