import time
import board
from loguru import logger
from dotenv import load_dotenv
import os

from devices import DatabaseManager, RpiRelay, RpiDht11, RpiDs18b20, RpiLcd1602


# 加载环境变量
load_dotenv()

# 数据库配置
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}


def main():
    # 初始化数据库
    db = DatabaseManager(**DB_CONFIG)

    # 初始化传感器和继电器
    with (
        RpiDht11(board.D23) as dht11,
        RpiDs18b20() as ds18b20,
        RpiRelay(24) as relay,
        RpiLcd1602() as lcd,
    ):
        try:
            while True:
                # 读取温湿度数据
                dht_temperature, humidity = dht11.read()
                ds18_temperature = ds18b20.read()

                # 在LCD1602上显示温湿度
                if dht_temperature is not None and humidity is not None:
                    lcd.clear()
                    # 格式化显示字符串，保留一位小数
                    temp_str = f"Temp: {dht_temperature:.1f} C"
                    humi_str = f"Humi: {humidity:.1f} %"
                    lcd.write(0, 0, temp_str)
                    lcd.write(0, 1, humi_str)
                else:
                    lcd.clear()
                    lcd.write(0, 0, "Sensor Read Error")
                    lcd.write(0, 1, "Check DHT11!")

                # 插入数据库
                if ds18_temperature is not None and humidity is not None:
                    db.insert_env_data(ds18_temperature, humidity)

                # 根据温度控制继电器（示例逻辑：温度高于25度时开启继电器）
                if dht_temperature is not None:
                    if dht_temperature > 25:
                        relay.on()
                    else:
                        relay.off()

                # 等待2秒后继续下一次读取
                time.sleep(2)

        except KeyboardInterrupt:
            logger.info("用户终止程序")
        except Exception as e:
            logger.exception(f"运行时出错: {e}")


if __name__ == "__main__":
    main()
