# services/display_manager.py
import asyncio
from loguru import logger
from state import shared_state
from config import settings


class DisplayManager:
    def __init__(self):
        logger.info("DisplayManager: 初始化完成 (模拟模式)")

    async def run(self):
        """模拟LCD屏幕更新循环"""
        logger.info("DisplayManager: 开始屏幕更新循环...")
        while True:
            # 从共享状态读取数据并“显示”它
            temp = shared_state.get("temperature", "N/A")
            hum = shared_state.get("humidity", "N/A")
            smoke = shared_state.get("smoke_level", "N/A")

            # 在真实场景中，这里会是控制LCD屏幕的代码
            # 现在我们只是打印到控制台
            # 只有当smoke是数字时才使用.2f格式化
            smoke_str = (
                f"{smoke:.2f}" if isinstance(smoke, (int, float)) else str(smoke)
            )
            logger.info(f"\n[模拟LCD显示] T:{temp}°C  H:{hum}%  S:{smoke_str}\n")

            await asyncio.sleep(settings.DISPLAY_UPDATE_INTERVAL)
