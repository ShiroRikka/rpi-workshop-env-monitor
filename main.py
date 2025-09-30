import time
import board
from devices import relay, rpi_dht11, rpi_relay

# 主程序
if __name__ == "__main__":
    dht11 = rpi_dht11(board.D14)
    relay = rpi_relay(15)
    while True:
        tem, hum = dht11.read()
        if tem is None or hum is None:
            time.sleep(1)
            continue
          
        if (tem >= 30 or hum >= 80) and not relay.is_status:
            relay.on()
        elif tem < 30 and hum < 80 and relay.is_status:
            relay.off()

        time.sleep(1)