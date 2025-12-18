from loguru import logger
from src.hardware.dht_11 import dht_inst
import asyncio


async def main():
    while True:
        temperature, humidity = await dht_inst.read()
        logger.info(f"温度：{temperature} C,湿度：{humidity} %")


asyncio.run(main())
