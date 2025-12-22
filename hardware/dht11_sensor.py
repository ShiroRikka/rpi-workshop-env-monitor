from .base_sensor import BaseSensor
import adafruit_dht
import board


class DHT11Sensor(BaseSensor):
    def __init__(self, pin: board.pin, mode: str):
        super().__init__()
        self.pin = pin
        self.dht_device = adafruit_dht.DHT11(self.pin)
        self._mode: str = mode  # 'temp' 或 'humid'

    async def read(self):
        """DHT11 传感器读取温度或湿度数据

        Args:
            mode (str): 读取模式，'temp' 读取温度，'humid' 读取湿度.

        Returns:
            self._value: 返回读取的温度或湿度值，读取失败时返回 None.
        """
        if self._mode == "temp":
            self._value = await self._read_temp()
        elif self._mode == "humid":
            self._value = await self._read_humid()
        return self._value

    async def _read_temp(self):
        return (
            self.dht_device.temperature
            if self.dht_device.temperature is not None
            else None
        )

    async def _read_humid(self):
        return (
            self.dht_device.humidity if self.dht_device.humidity is not None else None
        )
