import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    model_name: str = os.getenv("MODEL_NAME", "gemini-2.0-flash")
    max_tokens: int = int(os.getenv("MAX_TOKENS", "4096"))
    max_agent_iterations: int = int(os.getenv("MAX_AGENT_ITERATIONS", "10"))
    database_url: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/chatapp")
    qdrant_url: str = os.getenv("QDRANT_URL", "http://localhost:6333")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "embedding-001")
