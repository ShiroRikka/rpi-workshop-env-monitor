from .base_sensor import BaseSensor
import asyncio
import adafruit_dht
import board


class DHT11Sensor(BaseSensor):
    def __init__(self, pin: board.pin):
        super().__init__(pin)
        self.dht_device = adafruit_dht.DHT11(self.pin)

    async def read(self):
        temperature = self.dht_device.temperature
        humidity = self.dht_device.humidity
        if temperature is not None and humidity is not None:
            self._value = {"temperature": temperature, "humidity": humidity}
        else:
            return None
        await asyncio.sleep(2)
        return self._value
