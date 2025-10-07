import time
from w1thermsensor import W1ThermSensor
from w1thermsensor.errors import NoSensorFoundError, SensorNotReadyError


class RpiDs18b20:
    def __init__(self):
        try:
            self.sensor = W1ThermSensor()
        except NoSensorFoundError:
            print("错误: 未检测到任何DS18B20传感器。请检查硬件连接。")
            self.sensor = None
        except Exception as e:
            print(f"初始化传感器时发生未知错误: {e}")
            self.sensor = None

    def read(self):
        if self.sensor is None:
            return None
        try:
            temperature = self.sensor.get_temperature()
            return temperature
        except SensorNotReadyError:
            print("警告：传感器尚未就绪，请稍后再试。")
            return None
        except Exception as e:
            print(f"读取温度时发生未知错误: {e}")
            return None


if __name__ == "__main__":
    ds18b20 = RpiDs18b20()
    if ds18b20.sensor is None:
        print("程序退出：无法初始化传感器。")
        exit(1)

    try:
        while True:
            temperature = ds18b20.read()
            if temperature is not None:
                print(f"温度: {temperature:.2f} °C")
            else:
                print("温度读取失败，等待下一次尝试...")
            time.sleep(2)
    except KeyboardInterrupt:
        print("\n程序已由用户中断。")
    finally:
        print("清理资源并退出。")
