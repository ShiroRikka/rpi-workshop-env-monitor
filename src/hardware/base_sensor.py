from abc import ABC, abstractmethod


class BaseSensor(ABC):
    @abstractmethod
    async def read(self) -> float | tuple[int | float | None, int | float | None]:
        pass
