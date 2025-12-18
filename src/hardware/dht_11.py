from src.hardware.base_sensor import BaseSensor
import asyncio
import adafruit_dht
from config import Config


class Dht_11(BaseSensor):
    async def read(self):
        dht = adafruit_dht.DHT11(Config.dht_11_pin)
        temperature = dht.temperature
        humidity = dht.humidity
        await asyncio.sleep(2)
        return temperature, humidity


dht_inst = Dht_11()
