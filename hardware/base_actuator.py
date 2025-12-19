from abc import ABC, abstractmethod


class BaseActuator(ABC):
    """所有执行器的抽象基类"""

    def __init__(self, pin: int):
        self.pin = pin
        self._is_on = False

    @abstractmethod
    async def turn_on(self) -> None:
        """异步打开执行器"""
        pass

    @abstractmethod
    async def turn_off(self) -> None:
        """异步关闭执行器"""
        pass

    async def toggle(self):
        """异步切换执行器状态"""
        if self._is_on:
            await self.turn_off()
        else:
            await self.turn_on()
