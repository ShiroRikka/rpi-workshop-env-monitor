from gpiozero import OutputDevice
from loguru import logger
import time


class RpiRelay:
    """BCM模式下Raspberry Pi继电器控制器

    使用示例:
    >>> with RpiRelay(pin=15) as relay:
    ...     relay.on()      # 显式开启
    ...     time.sleep(5)   # 保持开启5秒
    ...     # 退出with块时自动关闭

    注意事项:
    - 硬件操作前会检查当前状态避免重复操作
    - 异常时会尝试将继电器恢复到安全状态（关闭）
    - 推荐使用with语句确保资源正确释放，即使发生异常
    - 无效引脚范围(2-27)会在初始化时抛出ValueError
    """

    def __init__(self, pin: int = 15) -> None:
        if not (2 <= pin <= 27):
            raise ValueError("无效GPIO引脚，请使用BCM编号2-27")
        self.relay = OutputDevice(pin)
        self.relay.off()  # 确保初始状态为关闭
        logger.info(f"继电器初始化: GPIO{pin}，初始状态：关闭")

    def on(self) -> None:
        """激活继电器（仅当未激活时操作）"""
        if not self.is_on:
            self.relay.on()
            logger.info(f"继电器已激活 ({self.relay.pin})")

    def off(self) -> None:
        """关闭继电器（仅当激活时操作）"""
        if self.is_on:
            self.relay.off()
            logger.info(f"继电器已关闭 ({self.relay.pin})")

    def toggle(self) -> None:
        self.relay.toggle()
        status = "激活" if self.is_on else "关闭"
        logger.info(f"继电器状态已切换 ({self.relay.pin})，当前状态：{status}")

    def close(self) -> None:
        """关闭继电器并释放资源"""
        self.relay.close()
        logger.info(f"继电器资源已释放 (GPIO{self.relay.pin})")

    @property
    def is_on(self) -> bool:
        return self.relay.is_active

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.close()
        except Exception as e:
            logger.error(f"释放继电器资源失败: {e}")


if __name__ == "__main__":
    try:
        with RpiRelay(24) as relay:
            relay.on()
            time.sleep(2)
            relay.toggle()
            time.sleep(2)
    except KeyboardInterrupt:
        logger.info("用户中断")
    except Exception as e:
        logger.error(f"运行时出错: {e}")
