import time
import board
from devices import rpi_dht11, rpi_relay

# 主程序
if __name__ == "__main__":
    dht11 = rpi_dht11(board.D14)
    while True:
        dht11.read()
        time.sleep(1)
