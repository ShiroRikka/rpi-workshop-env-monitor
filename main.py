import time
from devices.dht import read_dht11_circuitpython


# 主程序
if __name__ == "__main__":
    while True:
        read_dht11_circuitpython()
        time.sleep(1)
