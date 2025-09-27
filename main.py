import devices


def init_devices():
    ds18b20 = devices.DS18B20()
    mq2 = devices.MQ2()
    dht11 = devices.DHT11()
    return ds18b20, mq2, dht11


if __name__ == "__main__":
    DS18B20, MQ2, DHT11 = init_devices()

    DS18B20.read_temperature()
    MQ2.read_analog()
    MQ2.read_digital()
    DHT11.read_humidity()
    DHT11.read_temperature()
