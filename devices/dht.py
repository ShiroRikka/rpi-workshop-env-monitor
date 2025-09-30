import time
import board
import adafruit_dht
from loguru import logger


class rpi_dht11:
    def __init__(self, pin=board.D14):
        self.pin = pin
        self.sensor = adafruit_dht.DHT11(self.pin)

    def read(self):
        """

        :return: 温度,湿度
        """
        try:
            temperature = self.sensor.temperature
            humidity = self.sensor.humidity

            if temperature is not None and humidity is not None:
                logger.success(f"温度: {temperature:.1f}°C")
                logger.success(f"湿度: {humidity:.1f}%")
                return temperature, humidity
            else:
                logger.error("读取失败")
                return None, None

        except RuntimeError as e:
            logger.error(f"读取错误: {e.args[0]}")
            return None, None
        except Exception as e:
            logger.error(f"其他错误: {e}")
            return None, None


# 测试
if __name__ == "__main__":
    dht11 = rpi_dht11(board.D14)
    while True:
        dht11.read()
        time.sleep(2)
