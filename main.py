import time
import board
from loguru import logger
from dotenv import load_dotenv
import os

from devices import DatabaseManager, RpiRelay, RpiDht11


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
    with RpiDht11(board.D14) as dht11, RpiRelay(15) as relay:
        try:
            while True:
                # 读取温湿度数据
                temperature, humidity = dht11.read()

                # 插入数据库
                if temperature is not None and humidity is not None:
                    db.insert_env_data(temperature, humidity)

                # 根据温度控制继电器（示例逻辑：温度高于25度时开启继电器）
                if temperature is not None:
                    if temperature > 25:
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
