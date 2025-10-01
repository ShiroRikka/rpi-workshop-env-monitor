# /relay.py
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

    注意:
    - 硬件操作前会检查当前状态避免重复
    - 异常时自动关闭继电器保证安全
    """

    def __init__(self, pin: int = 15):
        self.relay = OutputDevice(pin)
        logger.info(f"继电器初始化: GPIO{pin}")

    def on(self):
        """激活继电器（仅当未激活时操作）"""
        if not self.is_on:
            self.relay.on()
            logger.info("继电器已激活")

    def off(self):
        """关闭继电器（仅当激活时操作）"""
        if self.is_on:
            self.relay.off()
            logger.info("继电器已关闭")

    def toggle(self):
        """切换继电器状态"""
        self.off() if self.is_on else self.on()

    @property
    def is_on(self) -> bool:
        """返回当前继电器状态"""
        return self.relay.value

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.off()
        except Exception as e:
            logger.error(f"关闭继电器时出错: {e}")

        try:
            self.relay.close()
        except Exception as e:
            logger.error(f"释放GPIO资源失败: {e}")

        return False


if __name__ == "__main__":
    with RpiRelay(15) as relay:
        relay.on()
        time.sleep(2)
