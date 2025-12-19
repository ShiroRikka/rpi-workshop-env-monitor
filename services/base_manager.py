from abc import ABC, abstractmethod


class BaseManager(ABC):
    def __init__(self, config, shared_state) -> None:
        self.config = config
        self.shared_state = shared_state

    @abstractmethod
    async def run(self):
        pass
