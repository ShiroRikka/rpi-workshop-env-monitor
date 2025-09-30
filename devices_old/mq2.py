import time

import RPi.GPIO as GPIO

from pcf8591 import PCF8591


class MQ2:
    """MQ2模块驱动"""

    def __init__(self, do=17):
        """
        :param do: MQ2模块数字IO口
        :type do: int
        """
        self.do = do
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        self.ADC = PCF8591()
        GPIO.setup(do, GPIO.IN)

    def read_analog(self):
        """读取MQ2模块模拟量值

        :return: 模拟量值,范围0-255
        :rtype: int
        """
        return self.ADC.read(0)

    def read_digital(self):
        """读取MQ2模块数字量值

        :return: 数字量值, 0或1
        :rtype: int
        """
        return GPIO.input(self.do)

    @staticmethod
    def cleanup():
        """释放GPIO资源"""
        GPIO.cleanup()


if __name__ == "__main__":
    mq2 = MQ2()
    try:
        while True:
            analog_value = mq2.read_analog()
            digital_value = mq2.read_digital()
            print(f"Analog: {analog_value}, Digital: {digital_value}")
            time.sleep(1)
    except KeyboardInterrupt:
        mq2.cleanup()
