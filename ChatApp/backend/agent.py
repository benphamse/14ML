"""
Agentic AI loop: sends messages to Gemini, handles function_call responses,
executes tools, and feeds results back until the agent produces a final text response.
Supports real-time streaming text chunks back to the client.
"""

import asyncio
import json
from concurrent.futures import ThreadPoolExecutor
from functools import partial

import google.generativeai as genai
from google.ai.generativelanguage_v1beta import types as glm_types

from config import GEMINI_API_KEY, MODEL_NAME, MAX_TOKENS, MAX_AGENT_ITERATIONS
from tools import GEMINI_TOOLS, execute_tool

genai.configure(api_key=GEMINI_API_KEY)

_executor = ThreadPoolExecutor(max_workers=4)

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


async def run_agent(conversation_history: list[dict], on_step=None):
    model = genai.GenerativeModel(
        model_name=MODEL_NAME,
        tools=GEMINI_TOOLS,
        system_instruction=SYSTEM_PROMPT,
        generation_config=genai.GenerationConfig(max_output_tokens=MAX_TOKENS),
    )

    gemini_history = _build_gemini_history(conversation_history[:-1])
    last_message = conversation_history[-1]
    user_text = last_message.get("content", "")

    chat = model.start_chat(history=gemini_history)
    iterations = 0

    full_response, function_calls = await _stream_message(chat, user_text, on_step)

    while iterations < MAX_AGENT_ITERATIONS:
        iterations += 1

        if not function_calls:
            conversation_history.append({
                "role": "assistant",
                "content": full_response,
            })
            return full_response, conversation_history

        function_responses = []
        for fc in function_calls:
            tool_name = fc["name"]
            tool_args = fc["args"]

            if on_step:
                await on_step({
                    "type": "tool_call",
                    "tool": tool_name,
                    "input": tool_args,
                })

            result = await execute_tool(tool_name, tool_args)

            if on_step:
                await on_step({
                    "type": "tool_result",
                    "tool": tool_name,
                    "result": json.dumps(result),
                })

            function_responses.append(
                glm_types.Part(
                    function_response=glm_types.FunctionResponse(
                        name=tool_name,
                        response=result,
                    )
                )
            )

        full_response, function_calls = await _stream_message(
            chat, function_responses, on_step
        )

    fallback = "I've reached the maximum number of steps. Here's what I found so far."
    conversation_history.append({"role": "assistant", "content": fallback})
    return fallback, conversation_history


async def _stream_message(chat, content, on_step=None):
    """
    Send a message with streaming. Uses a thread to iterate the sync generator
    and an asyncio.Queue to push chunks to the async consumer in real-time.
    """
    loop = asyncio.get_event_loop()
    queue: asyncio.Queue = asyncio.Queue()

    def _produce_chunks():
        """Runs in a thread: iterates the sync streaming response, pushing chunks to the queue."""
        import re
        import time
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
                    # Extract retry delay from error message
                    match = re.search(r"retry in (\d+\.?\d*)", err_str, re.IGNORECASE)
                    wait = float(match.group(1)) + 1 if match else 20
                    loop.call_soon_threadsafe(queue.put_nowait, (
                        "status", f"Rate limited. Retrying in {int(wait)}s..."
                    ))
                    time.sleep(wait)
                else:
                    loop.call_soon_threadsafe(queue.put_nowait, ("error", e))
                    return

    # Start producing chunks in a background thread
    loop.run_in_executor(_executor, _produce_chunks)

    # Consume chunks as they arrive
    full_text = ""
    function_calls = []

    while True:
        msg_type, payload = await queue.get()

        if msg_type == "done":
            break
        if msg_type == "error":
            raise payload
        if msg_type == "status":
            if on_step:
                await on_step({"type": "status", "content": payload})
            continue

        # payload is a streaming chunk
        chunk = payload
        for part in chunk.parts:
            if hasattr(part, "function_call") and part.function_call.name:
                function_calls.append({
                    "name": part.function_call.name,
                    "args": dict(part.function_call.args) if part.function_call.args else {},
                })
            elif hasattr(part, "text") and part.text:
                full_text += part.text
                if on_step:
                    await on_step({
                        "type": "stream",
                        "content": part.text,
                    })

    return full_text, function_calls


def _build_gemini_history(messages: list[dict]) -> list:
    history = []
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        gemini_role = "model" if role == "assistant" else "user"
        if isinstance(content, str) and content:
            history.append({"role": gemini_role, "parts": [content]})
    return history
