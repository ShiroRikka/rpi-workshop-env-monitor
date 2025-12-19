from abc import ABC, abstractmethod
from config import Settings


class BaseManager(ABC):
    def __init__(self, config: Settings, shared_state: dict) -> None:
        self.config = config
        self.shared_state = shared_state

    @abstractmethod
    async def run(self):
        pass
