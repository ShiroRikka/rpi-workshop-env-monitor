import time
from loguru import logger
from w1thermsensor import W1ThermSensor
from w1thermsensor.errors import NoSensorFoundError, SensorNotReadyError


class RpiDs18b20:
    def __init__(self):
        self.sensor = None
        logger.info("正在初始化 DS18B20 传感器...")
        self._initialize_sensor()

    def _initialize_sensor(self):
        """初始化DS18B20传感器"""
        try:
            self.sensor = W1ThermSensor()
            logger.info("DS18B20传感器初始化成功。")
        except NoSensorFoundError:
            logger.error("初始化失败：未检测到任何DS18B20传感器。请检查硬件连接。")
            self.sensor = None

    def __enter__(self):
        """进入 with 语句时调用"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出 with 语句时调用，进行清理"""
        logger.info("正在关闭DS18B20传感器连接。")
        self.sensor = None
        return False

    def read(self):
        """读取温度"""
        if not self.sensor:
            pass
            return None

        try:
            temperature = self.sensor.get_temperature()
            return temperature
        except SensorNotReadyError:
            logger.warning("DS18B20传感器尚未就绪，正在重试...")
            time.sleep(1)
        except Exception as e:
            logger.error(f"DS18B20读取温度时发生错误: {e}")
            time.sleep(10)
        return None


if __name__ == "__main__":
    with RpiDs18b20() as ds18b20:
        try:
            while True:
                temperature = ds18b20.read()
                if temperature is not None:
                    logger.info(f"温度: {temperature:.2f} °C")
                time.sleep(2)
        except KeyboardInterrupt:
            logger.info("程序已由用户中断。")
        finally:
            logger.info("程序退出。")
