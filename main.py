from loguru import logger
from src.dht import read_dht11
import asyncio


async def main():
    while True:
        temperature, humidity = await read_dht11()
        logger.info(f"温度：{temperature},湿度：{humidity}")


asyncio.run(main())
