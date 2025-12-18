# main.py
import asyncio
from loguru import logger

# 导入配置
from config import settings

# 导入共享状态

# 导入所有需要并发运行的服务
from services.data_manager import DataManager
from services.display_manager import DisplayManager

# from api.main_api import run_server
from state import shared_state


async def main():
    """
    主协程：负责初始化和启动所有后台服务
    """
    # 1. 配置全局日志
    # 就像你熟悉的 loguru 一样，在入口点配置一次，全局生效
    logger.info("=" * 50)
    logger.info("系统启动中...")
    logger.info("=" * 50)

    # 2. 初始化所有服务
    # 我们将共享状态和配置传递给需要它们的模块
    data_manager = DataManager(settings, shared_state)
    display_manager = DisplayManager()

    # 3. 使用 asyncio.gather 并发运行所有长期任务
    # 这就是你之前理解的精髓！
    # 每个任务都是一个独立的、长期运行的“串行链”
    # 它们会在同一个事件循环中并发执行，互不阻塞
    logger.info("正在启动所有核心任务...")
    try:
        await asyncio.gather(
            data_manager.run(),  # 任务1: 数据采集与控制循环
            display_manager.run(),  # 任务2: 屏幕显示更新循环
            # run_server(settings),  # 任务3: FastAPI Web服务
        )
    except Exception as e:
        logger.critical(f"某个核心服务发生致命错误，程序即将退出: {e}")

    logger.info("所有任务已结束。")


if __name__ == "__main__":
    # asyncio.run() 是启动整个异步应用的官方推荐方式
    # 它会创建一个新的事件循环，运行 main() 直到完成，然后清理循环
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # 捕获 Ctrl+C，实现优雅退出
        logger.info("程序被用户中断，正在安全关闭...")
