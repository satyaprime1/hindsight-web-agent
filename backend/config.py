import os
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv

# Load .env file from project root
ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")

class Settings(BaseModel):
    hindsight_api_key: str = os.getenv("HINDSIGHT_API_KEY", "")
    hindsight_base_url: str = os.getenv("HINDSIGHT_BASE_URL", "https://api.hindsight.vectorize.io")
    hindsight_bank_id: str = os.getenv("HINDSIGHT_BANK_ID", "local-biz-architect")
    
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    groq_model: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    
    port: int = int(os.getenv("PORT", "8000"))
    host: str = os.getenv("HOST", "127.0.0.1")

    @property
    def has_hindsight_credentials(self) -> bool:
        return bool(self.hindsight_api_key and self.hindsight_api_key.strip() and self.hindsight_api_key != "your_hindsight_api_key_here")

    @property
    def has_groq_credentials(self) -> bool:
        return bool(self.groq_api_key and self.groq_api_key.strip() and self.groq_api_key != "your_groq_api_key_here")

settings = Settings()
