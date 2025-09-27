import time

import RPi.GPIO as GPIO


class ActiveBuzzer:
    """有源蜂鸣器模块驱动"""

    def __init__(self, pin: int = 11):
        """初始化有源蜂鸣器

        :param pin: 连接蜂鸣器的GPIO引脚号, 默认11
        :type pin: int
        """
        self.pin = pin
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, GPIO.HIGH)

    def _on(self):
        GPIO.output(self.pin, GPIO.LOW)

    def _off(self):
        GPIO.output(self.pin, GPIO.HIGH)

    def beep(self, duration: float):
        """发出蜂鸣声

        :param duration: 蜂鸣声持续时间（秒）
        :type duration: float
        """
        self._on()
        time.sleep(duration)
        self._off()
        time.sleep(duration)

    def cleanup(self):
        """清理GPIO设置"""
        self._off()
        GPIO.cleanup()


if __name__ == "__main__":
    buzzer = ActiveBuzzer()
    try:
        while True:
            buzzer.beep(0.5)
    except KeyboardInterrupt:
        buzzer.cleanup()
