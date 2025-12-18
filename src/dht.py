import time
import board
import adafruit_dht

# 初始化传感器，假设连接到 GPIO 4
# 对于树莓派 5，如果遇到 libgpiod 错误，该库可能不稳定，建议用方案二
dhtDevice = adafruit_dht.DHT11(board.D23)

while True:
    try:
        # 获取温湿度
        temperature_c = dhtDevice.temperature
        humidity = dhtDevice.humidity

        print(f"温度: {temperature_c:.1f} C  湿度: {humidity}%")

    except RuntimeError as error:
        # DHT11 读取经常失败，这是正常的，捕获错误并重试即可
        print(error.args[0])
        time.sleep(2.0)
        continue
    except Exception as error:
        dhtDevice.exit()
        raise error

    time.sleep(2.0)
