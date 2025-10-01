import time
import board
import adafruit_dht
from loguru import logger
from typing import Optional, Tuple


class RpiDht11:
    """Raspberry Pi DHT11温湿度传感器控制器

    使用示例:
    >>> with RpiDht11(board.D14) as sensor:
    ...     temperature, humidity = sensor.read()
    ...     print(f"温度: {temperature}°C, 湿度: {humidity}%")

    注意事项:
    - DHT11传感器需要至少2秒的读取间隔
    - 读取可能因时序问题失败，本类实现自动重试机制
    - 推荐使用with语句确保资源正确释放
    """

    def __init__(
        self,
        pin=board.D14,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ):
        """初始化DHT11传感器


        :param pin: GPIO引脚，使用board库定义的引脚名
        :param  max_retries: 读取失败时的最大重试次数
        :param  retry_delay: 重试之间的延迟（秒）
        """
        self.pin = pin
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.sensor = adafruit_dht.DHT11(self.pin)
        logger.info(f"DHT11传感器初始化: GPIO{pin}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False

    def close(self):
        """关闭传感器，释放资源"""
        try:
            self.sensor.exit()
            logger.info("DHT11传感器资源已释放")
        except Exception as e:
            logger.error(f"释放DHT11传感器资源失败: {e}")

    def read(self) -> Tuple[Optional[float], Optional[float]]:
        """读取温度和湿度

        :Returns tuple: (温度, 湿度)，如果读取失败则返回(None, None)

        注意:
            DHT11传感器读取可能因时序问题失败，本方法会自动重试
        """
        for attempt in range(self.max_retries):
            try:
                temperature = self.sensor.temperature
                humidity = self.sensor.humidity

                if temperature is not None and humidity is not None:
                    logger.success(f"温度: {temperature:.1f}°C, 湿度: {humidity:.1f}%")
                    return temperature, humidity
                else:
                    logger.warning(f"读取为空值，尝试 {attempt + 1}/{self.max_retries}")

            except RuntimeError as e:
                logger.warning(
                    f"读取错误 (尝试 {attempt + 1}/{self.max_retries}): {e.args[0]}"
                )

            if attempt < self.max_retries - 1:
                time.sleep(self.retry_delay)

        logger.error("多次尝试后仍无法读取传感器数据")
        return None, None


# 测试
if __name__ == "__main__":
    try:
        with RpiDht11(board.D14) as dht11:
            while True:
                dht11.read()
                time.sleep(2)
    except KeyboardInterrupt:
        logger.info("用户终止程序")

