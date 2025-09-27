import time

import RPi.GPIO as GPIO


class Relay:
    """继电器模块驱动"""

    def __init__(self, pin: int = 11):
        """初始化继电器

        :param pin: 连接继电器的GPIO引脚号, 默认11
        :type pin: int
        """
        self.pin = pin
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, GPIO.LOW)

    def on(self):
        """打开继电器"""
        GPIO.output(self.pin, GPIO.HIGH)

    def off(self):
        """关闭继电器"""
        GPIO.output(self.pin, GPIO.LOW)

    def cleanup(self):
        """复位继电器(关闭并清理GPIO设置)"""
        self.off()
        GPIO.cleanup()


if __name__ == "__main__":
    relay = Relay()
    try:
        while True:
            relay.on()
            time.sleep(0.5)
            relay.off()
            time.sleep(0.5)
    except KeyboardInterrupt:
        relay.cleanup()
