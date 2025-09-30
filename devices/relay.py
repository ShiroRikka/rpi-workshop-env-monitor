from gpiozero import OutputDevice
import time
from loguru import logger


class rpi_relay:
    def __init__(self, pin: int = 15):
        """
        初始化继电器

        :param pin: GPIO引脚编号 (默认15)
        """
        self.pin = pin
        self.senser = OutputDevice(self.pin)

    def on(self):
        self.senser.on()
        logger.success("继电器通电")

    def off(self):
        self.senser.off()
        logger.success("继电器断电")


# 测试
if __name__ == "__main__":
    relay = rpi_relay(21)
    relay.on()
    time.sleep(2)
    relay.off()
