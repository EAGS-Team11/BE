from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

# --- Catatan: try/except untuk pydantic_settings dihapus karena sudah diinstal ---

class Settings(BaseSettings):
    # Security/Auth Settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database Settings (Wajib didefinisikan untuk dimuat dari .env)
    DB_USER: str
    DB_PASS: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    # --- FIX: Tambahkan field OPENROUTER_API_KEY untuk AI Grader (Penting!) ---
    OPENROUTER_API_KEY: Optional[str] = None 

    # Pydantic V2 Configuration (menggantikan class Config)
    model_config = SettingsConfigDict(
        env_file=".env",
        # Secara eksplisit mengabaikan variabel di .env yang tidak didefinisikan di atas, 
        # ini mengatasi masalah 'extra_forbidden' sebelumnya.
        extra="ignore" 
    )
    
    # Helper property untuk URL koneksi SQLAlchemy
    @property
    def DATABASE_URL(self) -> str:
        """
        Membangun URL database menggunakan format PostgreSQL dengan driver psycopg2.
        """
        # Menggunakan format psycopg2 yang sesuai dengan FastAPI/SQLAlchemy
        return f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

# Buat instance settings
settings = Settings()