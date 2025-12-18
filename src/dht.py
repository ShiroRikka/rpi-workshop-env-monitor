import time
from loguru import logger
import asyncio

# 前提：
# sudo nano /boot/firmware/config.txt
# 在末尾添加：dtoverlay=dht11,gpiopin=23
# sudo reboot


# 定义设备路径（通常是device0，如果有多个传感器可能是device1等）
SENSOR_PATH = "/sys/bus/iio/devices/iio:device0"


async def read_dht11():
    await asyncio.sleep(3)
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
