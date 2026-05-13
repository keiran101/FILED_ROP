from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    host: str = "0.0.0.0"
    port: int = 1158
    upload_dir: Path = Path("uploads")
    max_file_size_mb: int = 500
    rate_limit: int = 30        # max files per minute per IP (0 = disabled)
    bypass_password: str = ""              # password to bypass size limit (set via .env)
    device_name: str = "FileDrop"

    class Config:
        env_file = ".env"


settings = Settings()
settings.upload_dir.mkdir(exist_ok=True)
