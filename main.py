# main.py
import time
import board
import os
from dotenv import load_dotenv
from devices import relay, rpi_dht11, rpi_relay, DatabaseManager

# 加载 .env 文件中的环境变量
load_dotenv()

# 主程序
if __name__ == "__main__":
    db = DatabaseManager(
        os.getenv("DB_HOST"),
        int(os.getenv("DB_PORT")),
        os.getenv("DB_USER"),
        os.getenv("DB_PASSWORD"),
    )
    dht11 = rpi_dht11(board.D14)
    relay = rpi_relay(15)
    while True:
        tem, hum = dht11.read()
        if tem is None or hum is None:
            time.sleep(1)
            continue

        db.insert_env_data(tem, hum)
        if (tem >= 30 or hum >= 80) and not relay.is_status:
            relay.on()
        elif tem < 30 and hum < 80 and relay.is_status:
            relay.off()

        time.sleep(1)

