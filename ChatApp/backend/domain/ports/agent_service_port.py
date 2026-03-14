from abc import ABC, abstractmethod

from domain.entities.conversation import Conversation
from domain.ports.step_notifier_port import StepNotifier


class AgentService(ABC):
    @abstractmethod
    async def run(
        self, conversation: Conversation, notifier: StepNotifier, rag_context: str | None = None,
    ) -> str: ...
