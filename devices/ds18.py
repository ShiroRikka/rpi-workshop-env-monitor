import time
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
    print("开始监控 DS18B20 传感器...")

    try:
        while True:
            try:
                temperature = ds18b20_reader.read()
                if temperature is not None:
                    print(f"温度: {temperature:.2f} °C")
                time.sleep(2)
            except NoSensorFoundError:
                print("错误: 未检测到任何DS18B20传感器。请检查硬件连接。")
                time.sleep(10)
            except SensorNotReadyError:
                print("警告: 传感器尚未就绪，正在重试...")
                time.sleep(1)
            except Exception as e:
                print(f"发生未知错误: {e}")
                time.sleep(10)
    except KeyboardInterrupt:
        print("\n程序已由用户中断。")
    finally:
        print("程序退出。")
