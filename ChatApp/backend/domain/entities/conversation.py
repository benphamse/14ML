from domain.entities.message import Message


class Conversation:
    def __init__(self) -> None:
        self._messages: list[Message] = []

    @property
    def messages(self) -> list[Message]:
        return list(self._messages)

    def add_user_message(self, content: str) -> None:
        self._messages.append(Message.user(content))

    def add_assistant_message(self, content: str) -> None:
        self._messages.append(Message.assistant(content))

    def clear(self) -> None:
        self._messages.clear()

    def to_history_dicts(self) -> list[dict]:
        return [
            {"role": msg.role, "content": msg.content}
            for msg in self._messages
            if msg.content
        ]

    def to_llm_history(self) -> list[dict]:
        history = []
        for msg in self._messages:
            if not msg.content:
                continue
            llm_role = "model" if msg.role == "assistant" else "user"
            history.append({"role": llm_role, "parts": [msg.content]})
        return history

    def get_prior_history(self) -> list[dict]:
        if not self._messages:
            return []
        return [
            {"role": "model" if m.role == "assistant" else "user", "parts": [m.content]}
            for m in self._messages[:-1]
            if isinstance(m.content, str) and m.content
        ]

    def get_last_user_content(self) -> str:
        if self._messages and self._messages[-1].role == "user":
            return self._messages[-1].content
        return ""
