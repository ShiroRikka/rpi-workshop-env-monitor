import time
import board
from devices import relay, rpi_dht11, rpi_relay

# 主程序
if __name__ == "__main__":
    dht11 = rpi_dht11(board.D14)
    relay = rpi_relay(15)
    while True:
        tem,hum = dht11.read()
        if tem > 30:
            relay.on()
        else:
            relay.off()

        time.sleep(2)

