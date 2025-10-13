"""
用于驱动树莓派和 MCP3008 ADC 的 MQ-2 气体传感器类。

该类提供了读取 MQ-2 传感器模拟值和检测数字阈值状态的功能。
MQ-2 传感器可用于检测液化气、丙烷、氢气、酒精、烟雾等多种可燃气体。

:param do_pin: 连接到传感器数字输出引脚 (DO) 的树莓派 GPIO 引脚号。
:type do_pin: int
"""

from gpiozero import MCP3008, Button
from loguru import logger
import time


class RpiMq2:
    """
    用于驱动树莓派和 MCP3008 ADC 的 MQ-2 气体传感器类。

    该类提供了读取 MQ-2 传感器模拟值和检测数字阈值状态的功能。
    MQ-2 传感器可用于检测液化气、丙烷、氢气、酒精、烟雾等多种可燃气体。

    :param do_pin: 连接到传感器数字输出引脚 (DO) 的树莓派 GPIO 引脚号。
    :type do_pin: int
    """

    def __init__(self, do_pin: int = 17) -> None:
        """
        初始化 RpiMq2 实例。

        :param do_pin: 连接到传感器数字输出引脚 (DO) 的树莓派 GPIO 引脚号，默认为 17。
        :type do_pin: int
        """
        self.adc = MCP3008(channel=0)
        self.mq2do = Button(do_pin, pull_up=False)
        logger.info(f"MQ-2 传感器初始化完成。模拟通道: 0, 数字引脚: {do_pin}")

    def read_analog(self) -> int:
        """
        读取传感器的模拟原始值。

        通过 MCP3008 ADC 转换器读取 MQ-2 传感器的模拟输出 (AO)。
        注意：此值为 ADC 的原始读数 (0-1023)，并非直接的 PPM 浓度值。
        如需精确浓度，需要进行校准和复杂的公式计算。

        :return: 模拟值的原始 ADC 读数 (0-1023)。
        :rtype: int
        """
        value = self.adc.raw_value
        logger.info(f"模拟值 (Analog Raw Value): {value}")
        return value


if __name__ == "__main__":
    logger.info("程序启动，开始监听 MQ-2 传感器...")
    try:
        mq2_sensor = RpiMq2()
        while True:
            mq2_sensor.read_analog()
            time.sleep(2)
    except KeyboardInterrupt:
        logger.warning("程序被用户中断 (Ctrl+C)。")
    except Exception as e:
        logger.error(f"发生未知错误: {e}")
    finally:
        logger.info("程序结束。")
