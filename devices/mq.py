#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import smbus
import time
import RPi.GPIO as GPIO


class GasSensor:
    """一个用于控制PCF8591 ADC和气体传感器的类。

    该类封装了通过I2C与PCF8591模数转换器通信的逻辑，以及通过GPIO
    读取气体传感器数字信号和控制蜂鸣器的功能。它提供了一个简单的接口
    来读取模拟值、运行持续的危险气体检测循环，并在程序结束时清理资源。

    :param i2c_address: PCF8591模块的I2C地址。
    :type i2c_address: int
    :param digital_pin: 连接气体传感器数字输出引脚的BCM编号。
    :type digital_pin: int
    :param buzzer_pin: 连接蜂鸣器引脚的BCM编号。
    :type buzzer_pin: int
    """

    def __init__(self, i2c_address, digital_pin, buzzer_pin):
        """初始化GasSensor对象，设置I2C总线和GPIO引脚。"""
        self.i2c_address = i2c_address
        self.digital_pin = digital_pin
        self.buzzer_pin = buzzer_pin
        self.last_status = 1  # 记录上一次的传感器状态，1为安全，0为危险
        self.buzzer_toggle_counter = 0  # 用于蜂鸣器鸣叫的计数器

        # 初始化I2C总线 (Raspberry Pi 2/3/Zero/Zero W使用总线1)
        self.bus = smbus.SMBus(1)

        # 初始化GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.digital_pin, GPIO.IN)
        GPIO.setup(self.buzzer_pin, GPIO.OUT)
        # 初始关闭蜂鸣器 (假设高电平为关闭)
        GPIO.output(self.buzzer_pin, GPIO.HIGH)

    def _read_adc_channel(self, channel):
        """从PCF8591的指定通道读取模拟值。

        :param channel: 要读取的ADC通道，范围0-3。
        :type channel: int
        :return: 读取到的8位模拟值 (0-255)。
        :rtype: int
        """
        if not 0 <= channel <= 3:
            raise ValueError("ADC通道必须在0到3之间")
        try:
            # 启用指定通道的ADC
            self.bus.write_byte(self.i2c_address, 0x40 + channel)
            # 读取一次以启动转换
            self.bus.read_byte(self.i2c_address)
            # 再次读取以获取转换结果
            return self.bus.read_byte(self.i2c_address)
        except Exception as e:
            print(f"读取ADC地址 {hex(self.i2c_address)} 通道 {channel} 时出错: {e}")
            return -1

    def _write_dac_value(self, value):
        """向PCF8591的DAC写入一个模拟值。

        :param value: 要写入的模拟值，范围0-255。
        :type value: int
        """
        if not 0 <= value <= 255:
            raise ValueError("DAC值必须在0到255之间")
        try:
            self.bus.write_byte_data(self.i2c_address, 0x40, value)
        except Exception as e:
            print(f"向DAC地址 {hex(self.i2c_address)} 写入值 {value} 时出错: {e}")

    def _print_status_message(self, status):
        """根据传感器状态打印相应的消息。

        :param status: 传感器状态，1表示安全，0表示检测到危险气体。
        :type status: int
        """
        if status == 1:
            print("")
            print("   ******************")
            print("   *     安全~      *")
            print("   ******************")
            print("")
        elif status == 0:
            print("")
            print("   ************************")
            print("   * 检测到危险气体! *")
            print("   ************************")
            print("")

    def read_analog_value(self, channel=0):
        """读取指定ADC通道的模拟值。

        :param channel: 要读取的ADC通道，默认为0。
        :type channel: int
        :return: 8位模拟值 (0-255)，如果出错则返回-1。
        :rtype: int
        """
        return self._read_adc_channel(channel)

    def run_detection(self, delay=0.2):
        """运行气体检测循环。

        此方法会持续读取传感器的数字和模拟值。当检测到状态变化时，
        会打印消息。如果检测到危险气体，蜂鸣器会鸣响。

        :param delay: 每次检测之间的延时时间（秒）。
        :type delay: float
        """
        print("开始气体检测循环，按 Ctrl+C 退出。")
        try:
            while True:
                # 读取模拟值并打印
                analog_value = self.read_analog_value(0)
                print(f"模拟值: {analog_value}")

                # 读取数字IO口值
                current_status = GPIO.input(self.digital_pin)

                # 检查状态是否发生变化
                if current_status != self.last_status:
                    self._print_status_message(current_status)
                    self.last_status = current_status

                # 根据当前状态控制蜂鸣器
                if current_status == 0:  # 检测到危险气体
                    self.buzzer_toggle_counter += 1
                    # 通过高低电平交替变化使蜂鸣器发声
                    if self.buzzer_toggle_counter % 2 == 0:
                        GPIO.output(self.buzzer_pin, GPIO.HIGH)
                    else:
                        GPIO.output(self.buzzer_pin, GPIO.LOW)
                else:  # 安全状态
                    GPIO.output(self.buzzer_pin, GPIO.HIGH)  # 关闭蜂鸣器
                    self.buzzer_toggle_counter = 0  # 重置计数器

                time.sleep(delay)
        except KeyboardInterrupt:
            print("\n检测到中断信号，正在停止...")
        finally:
            self.cleanup()

    def cleanup(self):
        """清理GPIO资源，关闭蜂鸣器。"""
        print("正在清理资源...")
        GPIO.output(self.buzzer_pin, GPIO.HIGH)  # 确保蜂鸣器关闭
        GPIO.cleanup()
        print("资源清理完毕。")


if __name__ == "__main__":
    # 配置参数
    I2C_ADDRESS = 0x48  # PCF8591的I2C地址
    GAS_SENSOR_DO_PIN = 17  # 气体传感器数字输出引脚
    BUZZER_PIN = 18  # 蜂鸣器引脚

    try:
        # 创建GasSensor实例
        gas_detector = GasSensor(
            i2c_address=I2C_ADDRESS,
            digital_pin=GAS_SENSOR_DO_PIN,
            buzzer_pin=BUZZER_PIN,
        )
        # 运行检测循环
        gas_detector.run_detection()
    except Exception as e:
        print(f"程序运行出错: {e}")
    finally:
        # 确保在任何情况下都尝试清理资源
        if "gas_detector" in locals():
            gas_detector.cleanup()
