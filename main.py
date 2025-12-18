from loguru import logger
from hardware.dht11_sensor import DHT11Sensor
import asyncio


async def main():
    while True:
        temperature, humidity = await DHT11Sensor().read()
        logger.info(f"温度：{temperature} C,湿度：{humidity} %")


asyncio.run(main())
