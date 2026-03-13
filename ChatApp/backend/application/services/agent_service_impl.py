import json

from google.ai.generativelanguage_v1beta import types as glm_types

from domain.entities.conversation import Conversation
from domain.ports.agent_service_port import AgentService
from domain.ports.llm_port import LLMService
from domain.ports.step_notifier_port import StepNotifier
from domain.ports.tool_registry_port import ToolRegistryPort


class AgentServiceImpl(AgentService):
    def __init__(
        self,
        llm_service: LLMService,
        tool_registry: ToolRegistryPort,
        max_iterations: int,
    ) -> None:
        self._llm = llm_service
        self._registry = tool_registry
        self._max_iterations = max_iterations

    async def run(self, conversation: Conversation, notifier: StepNotifier) -> str:
        history = conversation.get_prior_history()
        user_text = conversation.get_last_user_content()

        chat = self._llm.create_chat(history)
        full_response, function_calls = await self._llm.stream_message(
            chat, user_text, notifier.notify
        )

        iterations = 0
        while iterations < self._max_iterations:
            iterations += 1

            if not function_calls:
                conversation.add_assistant_message(full_response)
                return full_response

            function_responses = []
            for fc in function_calls:
                tool_name = fc["name"]
                tool_args = fc["args"]

                await notifier.notify({
                    "type": "tool_call",
                    "tool": tool_name,
                    "input": tool_args,
                })

                tool = self._registry.get_tool(tool_name)
                result = await tool.execute(tool_args)

                await notifier.notify({
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

            full_response, function_calls = await self._llm.stream_message(
                chat, function_responses, notifier.notify
            )

        fallback = "I've reached the maximum number of steps. Here's what I found so far."
        conversation.add_assistant_message(fallback)
        return fallback
