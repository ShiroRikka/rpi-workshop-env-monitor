import time
from loguru import logger
from w1thermsensor import W1ThermSensor
from w1thermsensor.errors import NoSensorFoundError, SensorNotReadyError


class RpiDs18b20:
    def __init__(self):
        self.sensor = None

    def read(self):
        try:
            if self.sensor is None:
                self.sensor = W1ThermSensor()
            temperature = self.sensor.get_temperature()
            return temperature
        except NoSensorFoundError:
            raise
        except SensorNotReadyError:
            raise
        except Exception as e:
            raise RuntimeError(f"读取温度时发生未知错误: {e}") from e


if __name__ == "__main__":
    ds18b20_reader = RpiDs18b20()
    logger.info("开始监控 DS18B20 传感器...")

    try:
        while True:
            try:
                temperature = ds18b20_reader.read()
                if temperature is not None:
                    logger.info(f"温度: {temperature:.2f} °C")
                time.sleep(2)
            except NoSensorFoundError:
                logger.error("未检测到任何DS18B20传感器。请检查硬件连接。")
                time.sleep(10)
            except SensorNotReadyError:
                logger.warning("传感器尚未就绪，正在重试...")
                time.sleep(1)
            except Exception as e:
                logger.error(f"读取温度时发生未知错误: {e}")
                time.sleep(10)
    except KeyboardInterrupt:
        logger.info("程序已由用户中断。")
    finally:
        logger.info("程序退出。")
