#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import smbus
import time
import RPi.GPIO as GPIO


class GasSensor:
    """通过PCF8591 ADC和树莓派GPIO与气体传感器交互的类。

    该类封装了初始化PCF8591模数转换器、读取模拟和数字信号、
    以及持续监控传感器状态的功能。
    """

    def __init__(self, address=0x48, do_pin=17):
        """初始化气体传感器和PCF8591模块。

        :param address: PCF8591模块的I2C地址
        :type address: int
        :param do_pin: 连接到气体传感器数字输出的BCM GPIO引脚号
        :type do_pin: int
        """
        self.address = address
        self.do_pin = do_pin
        self.last_status = 1  # 初始状态设为安全
        try:
            # 初始化I2C总线 (对于RPI V1版本，使用SMBus(0))
            self.bus = smbus.SMBus(1)
            # 设置GPIO模式和引脚
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            GPIO.setup(self.do_pin, GPIO.IN)
        except Exception as e:
            print(f"初始化失败: {e}")
            raise

    def read_adc(self, channel):
        """从PCF8591读取指定的模拟通道值。

        :param channel: 要读取的模拟通道 (0, 1, 2, 或 3)
        :type channel: int
        :return: 0-255之间的模拟读数，如果发生错误则返回-1
        :rtype: int
        """
        if not 0 <= channel <= 3:
            print("错误: 通道选择范围是0-3")
            return -1
        try:
            # 选择并启动转换
            self.bus.write_byte(self.address, 0x40 | channel)
            # 读取上一次的转换结果（本次转换未完成）
            self.bus.read_byte(self.address)
            # 读取本次转换的结果
            return self.bus.read_byte(self.address)
        except Exception as e:
            print(f"读取ADC地址 0x{self.address:02X} 时出错: {e}")
            return -1

    def write_dac(self, value):
        """向PCF8591的数模转换器(DAC)写入一个值。

        :param value: 要写入的模拟值，范围为0-255
        :type value: int
        """
        try:
            temp = int(value)
            if 0 <= temp <= 255:
                self.bus.write_byte_data(self.address, 0x40, temp)
            else:
                print("错误: 写入值的范围是0-255")
        except Exception as e:
            print(f"写入DAC地址 0x{self.address:02X} 时出错: {e}")

    def _print_status_message(self, status):
        """根据状态打印相应的消息。

        :param status: 传感器的状态 (1 为安全, 0 为危险)
        :type status: int
        """
        if status == 1:  # 安全
            print("")
            print("   ******************")
            print("   *   安全 Safe~   *")
            print("   ******************")
            print("")
        elif status == 0:  # 检测到烟雾
            print("")
            print("   ************************")
            print("   * 检测到危险气体 Danger! *")
            print("   ************************")
            print("")

    def monitor(self, interval=0.2):
        """持续监控气体传感器的模拟和数字输出。

        :param interval: 每次读取之间的时间间隔（秒）
        :type interval: float
        """
        print(
            f"开始监控气体传感器 (I2C地址: 0x{self.address:02X}, DO引脚: {self.do_pin})..."
        )
        try:
            while True:
                # 读取模拟值 (通常连接到AIN0)
                analog_value = self.read_adc(0)
                print(f"模拟值 AIN0 = {analog_value}")

                # 读取数字IO口值
                digital_status = GPIO.input(self.do_pin)

                # 仅在状态改变时打印消息
                if digital_status != self.last_status:
                    self._print_status_message(digital_status)
                    self.last_status = digital_status

                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n监控已停止。")

    def cleanup(self):
        """释放GPIO资源。"""
        print("正在清理GPIO资源...")
        GPIO.cleanup()

    def __enter__(self):
        """支持 with 语句的入口。"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """支持 with 语句的出口，自动清理资源。"""
        self.cleanup()


if __name__ == "__main__":
    try:
        # 使用 'with' 语句可以确保程序退出时自动调用 cleanup() 释放资源
        with GasSensor() as sensor:
            # 示例1: 监控气体传感器
            sensor.monitor(interval=0.5)

    except Exception as e:
        print(f"发生未预期的错误: {e}")
    finally:
        print("程序结束。")
