from abc import ABC, abstractmethod


class StepNotifier(ABC):
    @abstractmethod
    async def notify(self, step_data: dict) -> None: ...
