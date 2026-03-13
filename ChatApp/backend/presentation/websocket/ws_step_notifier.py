import json
from abc import abstractmethod

from fastapi import WebSocket

from domain.ports.step_notifier_port import StepNotifier


class BaseNotifier(StepNotifier):
    """Intermediate abstract class providing shared serialization for notifiers."""

    def serialize(self, step_data: dict) -> str:
        return json.dumps(step_data)

    @abstractmethod
    async def notify(self, step_data: dict) -> None: ...


class WsStepNotifier(BaseNotifier):
    def __init__(self, websocket: WebSocket) -> None:
        self._ws = websocket

    async def notify(self, step_data: dict) -> None:
        await self._ws.send_text(self.serialize(step_data))


class ListStepNotifier(BaseNotifier):
    def __init__(self) -> None:
        self._steps: list[dict] = []

    async def notify(self, step_data: dict) -> None:
        self._steps.append(step_data)

    @property
    def steps(self) -> list[dict]:
        return list(self._steps)
