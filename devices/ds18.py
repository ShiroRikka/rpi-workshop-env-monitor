import time
from loguru import logger
from w1thermsensor import W1ThermSensor
from w1thermsensor.errors import NoSensorFoundError, SensorNotReadyError


class RpiDs18b20:
    def __init__(self):
        self.sensor = None

    def __enter__(self):
        """进入 with 语句时调用，初始化传感器。"""
        logger.info("正在初始化 DS18B20 传感器...")
        try:
            self.sensor = W1ThermSensor()
            logger.info("传感器初始化成功。")
            return self
        except NoSensorFoundError:
            logger.error("初始化失败：未检测到任何DS18B20传感器。请检查硬件连接。")
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出 with 语句时调用，进行清理。"""
        logger.info("正在关闭传感器连接。")
        self.sensor = None
        return False

    def read(self):
        """读取温度。"""
        try:
            temperature = self.sensor.get_temperature()
            return temperature
        except SensorNotReadyError:
            raise
        except Exception as e:
            raise RuntimeError(f"读取温度时发生未知错误: {e}") from e


if __name__ == "__main__":
    try:
        with RpiDs18b20() as ds18b20_reader:
            logger.info("开始监控 DS18B20 传感器...")
            while True:
                try:
                    temperature = ds18b20_reader.read()
                    if temperature is not None:
                        logger.info(f"温度: {temperature:.2f} °C")
                    time.sleep(2)
                except SensorNotReadyError:
                    logger.warning("传感器尚未就绪，正在重试...")
                    time.sleep(1)
                except Exception as e:
                    logger.error(f"读取温度时发生错误: {e}")
                    time.sleep(10)
    except NoSensorFoundError:
        logger.error("程序因未找到传感器而退出。")
    except KeyboardInterrupt:
        logger.info("程序已由用户中断。")
    finally:
        logger.info("程序退出。")