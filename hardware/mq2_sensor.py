from .base_sensor import BaseSensor
from gpiozero import MCP3008


class MQ2Sensor(BaseSensor):
    """MQ2气体传感器，用于检测可燃气体浓度"""

    def __init__(self, channle: int):
        """
        初始化MQ2传感器

        Args:
            pin: MCP3008 ADC转换器的通道号
        """
        super().__init__()
        self.device = MCP3008(channle)

    async def read(self) -> int:
        """
        读取传感器数据并返回映射后的值

        Returns:
            int: 映射到0-255范围的气体浓度值
        """
        raw_value = self.device.value
        mapped_value = self._map_value(raw_value, 0, 1, 0, 255)
        self._value = round(mapped_value)
        return self._value

    @staticmethod
    def _map_value(
        x: float, in_min: float, in_max: float, out_min: float, out_max: float
    ) -> float:
        """
        将一个值从一个范围映射到另一个范围

        Args:
            x: 要映射的值
            in_min: 输入范围的最小值
            in_max: 输入范围的最大值
            out_min: 输出范围的最小值
            out_max: 输出范围的最大值

        Returns:
            float: 映射后的值
        """
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
