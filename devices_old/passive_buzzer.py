import time

import RPi.GPIO as GPIO


class PassiveBuzzer:
    """无源蜂鸣器模块驱动"""

    def __init__(self, pin: int = 11):
        """初始化无源蜂鸣器

        :param pin: 连接无源蜂鸣器的GPIO引脚编号,默认为11
        :type pin: int
        """
        self.pin = pin
        GPIO.setmode(GPIO.BOARD)  # 使用物理引脚编号
        GPIO.setwarnings(False)  # 关闭GPIO警告
        GPIO.setup(self.pin, GPIO.OUT)  # 设置引脚为输出模式
        self.buzzer = GPIO.PWM(self.pin, 440)  # 初始频率为440Hz
        self.buzzer.start(50)  # 以50%的占空比启动蜂鸣器

    def play_tone(self, frequency: int, duration: float):
        """播放指定频率和持续时间的音调

        :param frequency: 音调频率，单位为赫兹(Hz)
        :type frequency: int
        :param duration: 音调持续时间，单位为秒
        :type duration: float
        """
        self.buzzer.ChangeFrequency(frequency)  # 设置音调频率
        time.sleep(duration)  # 持续指定时间

    def stop(self):
        """停止蜂鸣器并清理GPIO资源"""
        self.buzzer.stop()  # 停止蜂鸣器
        GPIO.output(self.pin, 1)  # 设置引脚为高电平
        GPIO.cleanup()  # 清理GPIO资源


if __name__ == "__main__":
    buzzer = PassiveBuzzer(pin=11)  # 创建蜂鸣器实例，连接到引脚11
    try:
        # 播放一系列音调
        buzzer.play_tone(262, 0.5)  # C4
        buzzer.play_tone(294, 0.5)  # D4
        buzzer.play_tone(330, 0.5)  # E4
        buzzer.play_tone(349, 0.5)  # F4
        buzzer.play_tone(392, 0.5)  # G4
        buzzer.play_tone(440, 0.5)  # A4
        buzzer.play_tone(494, 0.5)  # B4
        buzzer.play_tone(523, 0.5)  # C5
    except KeyboardInterrupt:
        pass
    finally:
        buzzer.stop()  # 停止蜂鸣器并清理资源
