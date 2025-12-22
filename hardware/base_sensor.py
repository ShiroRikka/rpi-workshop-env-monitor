from abc import ABC, abstractmethod


class BaseSensor(ABC):
    """所有传感器的抽象基类"""

    def __init__(self):
        self._value = None

    @abstractmethod
    async def read(self) -> int | float | None:
        """
        异步读取传感器数据。
        所有子类都必须实现这个方法。
        """
        pass
