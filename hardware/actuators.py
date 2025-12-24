from .base_actuator import BaseActuator
import board
from gpiozero import DigitalOutputDevice, Motor
import asyncio
from loguru import logger


class RpiRelay(BaseActuator):
    def __init__(self, pin=board.pin):
        super().__init__(pin)
        self.device = DigitalOutputDevice(pin, active_high=True, initial_value=False)
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


class RpiMotor(BaseActuator):
    def __init__(self, forward_pin: int, backward_pin: int, enable_pin: int):
        self.device = Motor(
            forward=forward_pin, backward=backward_pin, enable=enable_pin, pwm=True
        )
        self._is_on = self.device.value

    async def turn_on(self, speed: float = 1.0) -> None:
        await asyncio.to_thread(self.device.forward, speed)
        self._is_on = True
        logger.debug(f"电机已打开，速度: {speed}")
        return None

    async def turn_off(self) -> None:
        await asyncio.to_thread(self.device.stop)
        self._is_on = False
        logger.debug("电机已关闭")
        return None
