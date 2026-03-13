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
