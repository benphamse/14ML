from abc import ABC, abstractmethod
from typing import Any, Callable, Awaitable


class LLMService(ABC):
    @abstractmethod
    async def stream_message(
        self,
        chat: Any,
        content: Any,
        on_chunk: Callable[[dict], Awaitable[None]] | None = None,
    ) -> tuple[str, list[dict]]: ...

    @abstractmethod
    def create_chat(self, history: list[dict]) -> Any: ...
