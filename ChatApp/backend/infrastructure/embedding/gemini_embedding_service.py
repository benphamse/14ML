import asyncio
from concurrent.futures import ThreadPoolExecutor

import google.generativeai as genai

from domain.ports.embedding_service_port import EmbeddingServicePort

_executor = ThreadPoolExecutor(max_workers=2)


class GeminiEmbeddingService(EmbeddingServicePort):
    def __init__(self, api_key: str, model_name: str = "text-embedding-004") -> None:
        genai.configure(api_key=api_key)
        self._model_name = model_name

    async def embed_text(self, text: str) -> list[float]:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            _executor,
            lambda: genai.embed_content(
                model=f"models/{self._model_name}",
                content=text,
                task_type="retrieval_document",
            ),
        )
        return result["embedding"]

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            _executor,
            lambda: genai.embed_content(
                model=f"models/{self._model_name}",
                content=texts,
                task_type="retrieval_document",
            ),
        )
        return result["embedding"]

    async def embed_query(self, text: str) -> list[float]:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            _executor,
            lambda: genai.embed_content(
                model=f"models/{self._model_name}",
                content=text,
                task_type="retrieval_query",
            ),
        )
        return result["embedding"]
