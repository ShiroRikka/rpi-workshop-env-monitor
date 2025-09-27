import time

import Adafruit_DHT


class DHT11:
    """DHT11传感器模块驱动"""

    def __init__(self, pin: int = 17):
        """初始化DHT11传感器

        :param pin: GPIO引脚编号, 默认17
        :type pin: int"""
        self.pin = pin
        self.sensor = Adafruit_DHT.DHT11

    def read(self):
        """从DHT11获取温度和湿度

        :return: 温度,湿度
        :rtype: tuple[float, float]
        """
        humidity, temperature = Adafruit_DHT.read_retry(self.sensor, self.pin)
        if humidity is not None and temperature is not None:
            return temperature, humidity
        else:
            raise RuntimeError("Failed to get reading. Try again!")


if __name__ == "__main__":
    sensor = DHT11()
    try:
        while True:
            temperature, humidity = sensor.read()
            print(f"Temp={temperature:0.1f}*C  Humidity={humidity:0.1f}%")
            time.sleep(1)
    except KeyboardInterrupt:
        pass
