from .base_actuator import BaseActuator
from gpiozero import DigitalOutputDevice, Motor
import asyncio
from loguru import logger


class RpiRelay(BaseActuator):
    def __init__(self, pin):
        super().__init__(pin)
        self.device = DigitalOutputDevice(pin, active_high=True, initial_value=False)
        self._is_on = self.device.value
        self._blink_task = None
        self._blink_enabled = False
        self._blink_interval = 0.5
        self._blink_duty_cycle = 0.5

    def configure_blink(
        self, enabled: bool, interval: float = 0.5, duty_cycle: float = 0.5
    ):
        """配置闪烁参数

        Args:
            enabled: 是否启用闪烁模式
            interval: 闪烁间隔（秒）
            duty_cycle: 闪烁占空比（0.0-1.0），1.0表示常亮
        """
        self._blink_enabled = enabled
        self._blink_interval = interval
        self._blink_duty_cycle = max(0.0, min(1.0, duty_cycle))  # 确保在有效范围内

    async def turn_on(self) -> None:
        if self._blink_enabled:
            # 启动闪烁任务
            if self._blink_task is None or self._blink_task.done():
                self._is_on = True
                self._blink_task = asyncio.create_task(self._blink_loop())
                logger.debug("报警闪烁已开启")
        else:
            # 常规开启
            await asyncio.to_thread(self.device.on)
            self._is_on = True
            logger.debug("报警已开启")
        return None

    async def turn_off(self) -> None:
        # 停止闪烁任务
        if self._blink_task and not self._blink_task.done():
            self._blink_task.cancel()
            try:
                await self._blink_task
            except asyncio.CancelledError:
                pass
            self._blink_task = None

        # 确保设备关闭
        await asyncio.to_thread(self.device.off)
        self._is_on = False
        logger.debug("报警已关闭")
        return None

    async def _blink_loop(self):
        """闪烁循环任务"""
        try:
            while True:
                # 计算开启和关闭时间
                on_time = self._blink_interval * self._blink_duty_cycle
                off_time = self._blink_interval * (1 - self._blink_duty_cycle)

                # 开启阶段
                if on_time > 0:
                    await asyncio.to_thread(self.device.on)
                    await asyncio.sleep(on_time)

                # 关闭阶段
                if off_time > 0:
                    await asyncio.to_thread(self.device.off)
                    await asyncio.sleep(off_time)

        except asyncio.CancelledError:
            # 任务被取消时确保设备关闭
            await asyncio.to_thread(self.device.off)
            raise


class RpiMotor(BaseActuator):
    def __init__(self, forward_pin: int, backward_pin: int, enable_pin: int):
        super().__init__(forward_pin)
        self.device = Motor(
            forward=forward_pin, backward=backward_pin, enable=enable_pin, pwm=True
        )
        self._is_on = self.device.value
        self._current_speed = 0.0

    async def turn_on(self, speed: float = 1.0) -> None:
        await asyncio.to_thread(self.device.forward, speed)
        self._is_on = True
        self._current_speed = speed
        logger.debug(f"电机已打开，速度: {speed}")
        return None

    async def turn_off(self) -> None:
        await asyncio.to_thread(self.device.stop)
        self._is_on = False
        self._current_speed = 0.0
        logger.debug("电机已关闭")
        return None

    async def set_speed(self, speed: float) -> None:
        """设置电机速度（电机必须已开启）"""
        if not self._is_on:
            logger.warning("尝试设置速度但电机未开启，将先开启电机")
            await self.turn_on(speed)
        else:
            await asyncio.to_thread(self.device.forward, speed)
            self._current_speed = speed
            logger.debug(f"电机速度已更新为: {speed}")
