import time
from loguru import logger

# 定义设备路径（通常是device0，如果有多个传感器可能是device1等）
SENSOR_PATH = "/sys/bus/iio/devices/iio:device0"


def read_dht11():
    try:
        # 读取温度 (单位是毫摄氏度，所以要除以1000)
        with open(f"{SENSOR_PATH}/in_temp_input", "r") as f:
            temp = float(f.read().strip()) / 1000.0

        # 读取湿度 (单位是毫百分比，所以要除以1000)
        with open(f"{SENSOR_PATH}/in_humidityrelative_input", "r") as f:
            hum = float(f.read().strip()) / 1000.0

        return temp, hum
    except Exception as e:
        print(f"读取错误: {e}")
        return None, None


while True:
    temperature, humidity = read_dht11()
    if temperature is not None:
        print(f"温度: {temperature:.1f}°C, 湿度: {humidity:.1f}%")
    else:
        print("传感器读取失败，重试中...")

    # DHT11 采样率很低，建议间隔至少2秒
    time.sleep(2)
