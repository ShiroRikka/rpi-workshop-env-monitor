"""DHT11温湿度传感器读取模块。

使用前提：
    sudo nano /boot/firmware/config.txt
    在末尾添加: dtoverlay=dht11,gpiopin=23
    sudo reboot
"""

import asyncio
from pathlib import Path

# 常量定义
SENSOR_PATH = Path("/sys/bus/iio/devices/iio:device0")
MILLIUNIT_CONVERSION_FACTOR = 1000.0
SENSOR_STABILIZATION_DELAY = 3  # 采样率间隔（秒）


def _read_sensor_value(file_path: Path) -> float:
    """从传感器文件读取并转换数值。

    Args:
        file_path: 传感器数据文件路径

    Returns:
        转换后的浮点数值
    """
    raw_value: float = 0
    while not raw_value:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                raw_value = float(f.read().strip())
                return raw_value / MILLIUNIT_CONVERSION_FACTOR
        except Exception:
            continue


async def read_dht11() -> tuple[float, float]:
    """异步读取DHT11温湿度传感器的温度和湿度值。

    在读取前会等待采样率间隔，然后分别读取温度和湿度数据。

    Returns:
        包含温度和湿度的元组 (temperature, humidity)。

    Example:
        >>> temp, hum = await read_dht11()
        ... print(f"温度: {temp}°C, 湿度: {hum}%")
    """
    await asyncio.sleep(SENSOR_STABILIZATION_DELAY)

    temp_file = SENSOR_PATH / "in_temp_input"
    humidity_file = SENSOR_PATH / "in_humidityrelative_input"

    temperature = _read_sensor_value(temp_file)
    humidity = _read_sensor_value(humidity_file)

    return temperature, humidity
