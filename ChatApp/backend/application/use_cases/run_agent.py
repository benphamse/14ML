from domain.entities.conversation import Conversation
from domain.ports.agent_service_port import AgentService
from domain.ports.step_notifier_port import StepNotifier


class RunAgentUseCase:
    def __init__(self, agent_service: AgentService) -> None:
        self._agent_service = agent_service

    async def execute(self, conversation: Conversation, notifier: StepNotifier) -> str:
        return await self._agent_service.run(conversation, notifier)
