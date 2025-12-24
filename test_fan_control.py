#!/usr/bin/env python3
"""
测试风扇控制逻辑的脚本
验证温度与风扇转速的映射关系是否正确
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import settings
from services.data_manager import DataManager


class MockSharedState:
    """模拟共享状态对象"""

    def update(self, data):
        print(f"共享状态更新: {data}")


class MockDatabase:
    """模拟数据库对象"""

    async def initialize(self):
        print("模拟数据库初始化")

    async def insert_reading(self, **kwargs):
        print(f"模拟数据插入: {kwargs}")


def test_fan_speed_calculation():
    """测试风扇转速计算逻辑"""
    print("=" * 50)
    print("测试风扇转速计算逻辑")
    print("=" * 50)

    # 创建模拟对象
    mock_shared_state = MockSharedState()
    mock_db = MockDatabase()

    # 创建 DataManager 实例
    data_manager = DataManager(settings, mock_shared_state)
    data_manager.db = mock_db

    # 测试不同温度下的风扇转速
    test_temperatures = [
        15.0,  # 低于最低温度
        18.0,  # 低于最低温度
        20.0,  # 等于最低温度
        22.0,  # 略高于最低温度
        25.0,  # 中间温度
        27.5,  # 中间温度
        30.0,  # 接近最高温度
        35.0,  # 等于最高温度
        40.0,  # 高于最高温度
    ]

    print("配置参数:")
    print(f"  最低温度: {settings.FAN_MIN_TEMP}°C")
    print(f"  最高温度: {settings.FAN_MAX_TEMP}°C")
    print(f"  最低转速: {settings.FAN_MIN_SPEED:.1%}")
    print(f"  最高转速: {settings.FAN_MAX_SPEED:.1%}")
    print()

    print("温度 -> 风扇转速映射:")
    print("-" * 30)

    for temp in test_temperatures:
        speed = data_manager._calculate_fan_speed(temp)
        status = "关闭" if speed <= 0 else f"{speed:.1%}"
        print(f"  {temp:5.1f}°C -> {status}")

    print()
    print("测试完成！")


if __name__ == "__main__":
    test_fan_speed_calculation()
