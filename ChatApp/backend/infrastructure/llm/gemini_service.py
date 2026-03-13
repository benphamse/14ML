import asyncio
import re
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, Awaitable

import google.generativeai as genai
from google.ai.generativelanguage_v1beta import types as glm_types

from domain.ports.llm_port import LLMService
from infrastructure.tools.registry import ToolRegistry

SYSTEM_PROMPT = """\
You are a helpful AI assistant with access to tools. You can:
- Search the web for current information
- Perform calculations
- Get the current date/time
- Create and save notes

When a user asks a question, think about whether you need to use any tools to provide a better answer. \
Use tools when they would be genuinely helpful, but respond directly when you already know the answer.

Be conversational, helpful, and concise. When using tools, explain what you're doing briefly.\
"""

_executor = ThreadPoolExecutor(max_workers=4)


class GeminiLLMService(LLMService):
    def __init__(
        self,
        api_key: str,
        model_name: str,
        max_tokens: int,
        tool_registry: ToolRegistry,
    ) -> None:
        genai.configure(api_key=api_key)
        self._model_name = model_name
        self._max_tokens = max_tokens
        self._tool_registry = tool_registry

    def create_chat(self, history: list[dict]) -> Any:
        model = genai.GenerativeModel(
            model_name=self._model_name,
            tools=self._tool_registry.get_gemini_tools(),
            system_instruction=SYSTEM_PROMPT,
            generation_config=genai.GenerationConfig(max_output_tokens=self._max_tokens),
        )
        return model.start_chat(history=history)

    async def stream_message(
        self,
        chat: Any,
        content: Any,
        on_chunk: Callable[[dict], Awaitable[None]] | None = None,
    ) -> tuple[str, list[dict]]:
        loop = asyncio.get_event_loop()
        queue: asyncio.Queue = asyncio.Queue()

        def _produce_chunks():
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = chat.send_message(content, stream=True)
                    for chunk in response:
                        loop.call_soon_threadsafe(queue.put_nowait, ("chunk", chunk))
                    loop.call_soon_threadsafe(queue.put_nowait, ("done", None))
                    return
                except Exception as e:
                    err_str = str(e)
                    if "429" in err_str and attempt < max_retries - 1:
                        match = re.search(r"retry in (\d+\.?\d*)", err_str, re.IGNORECASE)
                        wait = float(match.group(1)) + 1 if match else 20
                        loop.call_soon_threadsafe(
                            queue.put_nowait,
                            ("status", f"Rate limited. Retrying in {int(wait)}s..."),
                        )
                        time.sleep(wait)
                    else:
                        loop.call_soon_threadsafe(queue.put_nowait, ("error", e))
                        return

        loop.run_in_executor(_executor, _produce_chunks)

        full_text = ""
        function_calls: list[dict] = []

        while True:
            msg_type, payload = await queue.get()

            if msg_type == "done":
                break
            if msg_type == "error":
                raise payload
            if msg_type == "status":
                if on_chunk:
                    await on_chunk({"type": "status", "content": payload})
                continue

            chunk = payload
            for part in chunk.parts:
                if hasattr(part, "function_call") and part.function_call.name:
                    function_calls.append({
                        "name": part.function_call.name,
                        "args": dict(part.function_call.args) if part.function_call.args else {},
                    })
                elif hasattr(part, "text") and part.text:
                    full_text += part.text
                    if on_chunk:
                        await on_chunk({"type": "stream", "content": part.text})

        return full_text, function_calls
