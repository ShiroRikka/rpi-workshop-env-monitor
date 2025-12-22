import asyncio
import random
from .base_sensor import BaseSensor


class MockSmokeSensor(BaseSensor):
    """模拟烟雾传感器"""

    async def read(self):
        # 模拟硬件读取的延迟
        await asyncio.sleep(0.1)
        # 生成一个随机的烟雾值
        self._value = random.uniform(100, 800)
        return self._value


class MockTempSensor(BaseSensor):
    """模拟温度传感器（用于读取模拟信号）"""

    async def read(self):
        await asyncio.sleep(0.05)
        # 模拟一个0-40之间的ADC值
        self._value = random.randint(0, 44)
        return self._value
