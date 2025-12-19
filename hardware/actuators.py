from .base_actuator import BaseActuator
import board
from gpiozero import DigitalOutputDevice
import asyncio
from loguru import logger


class Relay(BaseActuator):
    def __init__(self, pin=board.pin):
        super().__init__(pin)
        self.device = DigitalOutputDevice(pin, active_high=False, initial_value=False)
        self._is_on = self.device.value

    async def turn_on(self) -> None:
        await asyncio.to_thread(self.device.on)
        self._is_on = True
        logger.info("继电器已打开")
        return None

    async def turn_off(self) -> None:
        await asyncio.to_thread(self.device.off)
        self._is_on = False
        logger.info("继电器已关闭")
        return None
