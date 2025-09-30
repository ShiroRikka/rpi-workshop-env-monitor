import time
import board
from devices.dht import rsi_dht11


# 主程序
if __name__ == "__main__":
    dht11 = rsi_dht11(board.D14)
    while True:
        dht11.read()
        time.sleep(1)
