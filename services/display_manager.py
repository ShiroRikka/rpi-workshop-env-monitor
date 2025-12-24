# services/display_manager.py
import asyncio
from loguru import logger
from .base_manager import BaseManager
from .lcd1602 import AsyncRpiLcd1602


class DisplayManager(BaseManager):
    def __init__(self, config, shared_state):
        super().__init__(config, shared_state)
        self.lcd = None
        self._lcd_address = config.LCD_ADDRESS
        self._lcd_bus = config.LCD_BUS_NUM
        self._lcd_cols = config.LCD_COLS
        self._lcd_rows = config.LCD_ROWS
        logger.info(
            f"DisplayManager: 初始化LCD显示器 (地址: 0x{self._lcd_address:02X}, {self._lcd_cols}x{self._lcd_rows})"
        )

    async def initialize(self):
        """异步初始化LCD显示器"""
        try:
            self.lcd = AsyncRpiLcd1602(
                address=self._lcd_address,
                backlight_on=True,
                bus_num=self._lcd_bus,
                cols=self._lcd_cols,
                rows=self._lcd_rows,
            )
            await self.lcd.initialize()
            await self.lcd.display_data("环境监控系统", "初始化完成...")
            logger.info("DisplayManager: LCD显示器初始化成功")
            await asyncio.sleep(2)  # 显示初始化信息
        except Exception as e:
            logger.error(f"DisplayManager: LCD初始化失败: {e}")
            raise

    async def run(self):
        """LCD屏幕更新循环"""
        await self.initialize()
        logger.info("DisplayManager: 开始屏幕更新循环...")

        while True:
            try:
                # 从共享状态读取数据
                temp = self._shared_state.get("temperature", "N/A")
                hum = self._shared_state.get("humidity", "N/A")
                smoke = self._shared_state.get("smoke_level", "N/A")
                fan_status = self._shared_state.get("fan_on", False)

                # 格式化显示数据
                line1 = self._format_line1(temp, hum)
                line2 = self._format_line2(smoke, fan_status)

                # 使用真实LCD显示
                await self.lcd.display_data(line1, line2, clear_first=True)

            except Exception as e:
                logger.error(f"DisplayManager: 显示更新失败: {e}")
                # 如果LCD出错，尝试重新初始化
                logger.info("DisplayManager: 尝试重新初始化LCD...")
                await self.initialize()

            await asyncio.sleep(self._config.DISPLAY_UPDATE_INTERVAL)

    def _format_line1(self, temp, hum):
        """格式化第一行显示内容（温度和湿度）"""
        # 使用0xDF作为摄氏度符号，这是LCD1602的标准做法
        degree_symbol = "\xdf"
        temp_str = (
            f"{temp:.1f}{degree_symbol}C"
            if isinstance(temp, (int, float))
            else f"{temp}{degree_symbol}C"
        )
        hum_str = f"{hum:.0f}%" if isinstance(hum, (int, float)) else f"{hum}%"
        return f"T:{temp_str} H:{hum_str}"

    def _format_line2(self, smoke, fan_status):
        """格式化第二行显示内容（烟雾和风扇状态）"""
        smoke_str = f"{smoke:.2f}" if isinstance(smoke, (int, float)) else str(smoke)
        fan_str = "on" if fan_status else "off"
        return f"S:{smoke_str} F:{fan_str}"

    async def cleanup(self):
        """清理资源"""
        if self.lcd:
            try:
                await self.lcd.display_data("系统关闭", "再见...")
                await asyncio.sleep(1)
                self.lcd.close()
                logger.info("DisplayManager: LCD资源已清理")
            except Exception as e:
                logger.error(f"DisplayManager: 清理LCD资源时出错: {e}")
