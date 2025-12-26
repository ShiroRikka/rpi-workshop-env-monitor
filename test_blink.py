#!/usr/bin/env python3
"""
测试警报闪烁功能的脚本
"""

import asyncio
import sys
from loguru import logger

# 添加项目根目录到路径
sys.path.append(".")

from config import settings
from hardware.actuators import RpiRelay


async def test_blink():
    """测试闪烁功能"""
    logger.info("开始测试警报闪烁功能...")

    # 创建警报继电器实例
    warning = RpiRelay(settings.WARNING_PIN)

    # 配置闪烁参数
    warning.configure_blink(
        enabled=settings.WARNING_BLINK_ENABLED,
        interval=settings.WARNING_BLINK_INTERVAL,
        duty_cycle=settings.WARNING_BLINK_DUTY_CYCLE,
    )

    logger.info(
        f"闪烁配置: 启用={settings.WARNING_BLINK_ENABLED}, "
        f"间隔={settings.WARNING_BLINK_INTERVAL}秒, "
        f"占空比={settings.WARNING_BLINK_DUTY_CYCLE}"
    )

    try:
        # 测试闪烁模式
        logger.info("开启闪烁模式...")
        await warning.turn_on()

        # 运行5秒
        await asyncio.sleep(5)

        # 关闭
        logger.info("关闭警报...")
        await warning.turn_off()

        # 等待1秒
        await asyncio.sleep(1)

        # 测试常亮模式（禁用闪烁）
        logger.info("测试常亮模式...")
        warning.configure_blink(enabled=False)
        await warning.turn_on()

        # 运行3秒
        await asyncio.sleep(3)

        # 关闭
        logger.info("关闭警报...")
        await warning.turn_off()

        logger.info("测试完成!")

    except KeyboardInterrupt:
        logger.info("测试被用户中断")
        await warning.turn_off()
    except Exception as e:
        logger.error(f"测试过程中发生错误: {e}")
        await warning.turn_off()


if __name__ == "__main__":
    # 配置日志
    logger.remove()
    logger.add(sys.stderr, level="INFO")

    # 运行测试
    asyncio.run(test_blink())
