import smbus
import asyncio


class RpiLcd1602:
    """
    用于通过I2C接口控制LCD1602显示器的类。
    该类封装了与基于PCF8574 I/O扩展器的I2C LCD模块进行通信所需的所有功能。
    """

    # I2C设备默认地址
    DEFAULT_ADDRESS = 0x27

    # LCD命令常量
    LCD_CLEARDISPLAY = 0x01
    LCD_RETURNHOME = 0x02
    LCD_ENTRYMODESET = 0x04
    LCD_DISPLAYCONTROL = 0x08
    LCD_CURSORSHIFT = 0x10
    LCD_FUNCTIONSET = 0x20
    LCD_SETCGRAMADDR = 0x40
    LCD_SETDDRAMADDR = 0x80

    # 显示控制标志
    LCD_DISPLAYON = 0x04
    LCD_DISPLAYOFF = 0x00
    LCD_CURSORON = 0x02
    LCD_CURSOROFF = 0x00
    LCD_BLINKON = 0x01
    LCD_BLINKOFF = 0x00

    # 功能集标志
    LCD_8BITMODE = 0x10
    LCD_4BITMODE = 0x00
    LCD_2LINE = 0x08
    LCD_1LINE = 0x00
    LCD_5x10DOTS = 0x04
    LCD_5x8DOTS = 0x00

    # I2C控制位
    BACKLIGHT = 0x08
    ENABLE = 0x04
    READ_WRITE = 0x02
    REGISTER_SELECT = 0x01

    def __init__(
        self, address=DEFAULT_ADDRESS, backlight_on=True, bus_num=1, cols=16, rows=2
    ):
        """
        初始化LCD1602显示器。

        :param address: LCD模块的I2C地址。
        :type address: int
        :param backlight_on: 是否开启背光，默认为True。
        :type backlight_on: bool
        :param bus_num: I2C总线编号，通常为1。
        :type bus_num: int
        """
        self.addr = address
        self.bus = None
        self.backlight_on = backlight_on
        self._initialized = False
        self.LCD_COLS = cols
        self.LCD_ROWS = rows

        try:
            self.bus = smbus.SMBus(bus_num)
        except Exception as e:
            self.close()
            raise IOError(f"I2C总线初始化失败: {e}")

    async def initialize(self):
        """异步初始化LCD显示器"""
        if not self._initialized:
            try:
                await self._init_display()
                self._initialized = True
            except Exception as e:
                self.close()
                raise IOError(f"LCD初始化失败: {e}")

    def _write_word(self, data):
        """
        向I2C设备写入一个字节数据，并根据背光状态设置控制位。
        这是一个内部辅助方法。

        :param data: 要写入的字节数据。
        :type data: int
        """
        if self.backlight_on:
            data |= self.BACKLIGHT
        else:
            data &= ~self.BACKLIGHT
        self.bus.write_byte(self.addr, data)

    async def _send_4bits(self, data):
        """
        发送4位数据到LCD。

        :param data: 要发送的4位数据。
        :type data: int
        """
        data |= self.ENABLE
        self._write_word(data)
        await asyncio.sleep(0.001)  # 减少延时，提高时序精度
        data &= ~self.ENABLE
        self._write_word(data)
        await asyncio.sleep(0.001)  # 添加延时确保稳定

    async def _send_command(self, comm):
        """
        向LCD发送一个命令。
        这是通过4位数据模式分两次发送（高4位和低4位）来实现的。
        这是一个内部辅助方法。

        :param comm: 要发送的命令字节。
        :type comm: int
        """
        # 发送高4位，确保RS=0（命令模式）
        await self._send_4bits(comm & 0xF0)
        # 发送低4位
        await self._send_4bits((comm << 4) & 0xF0)
        await asyncio.sleep(0.001)  # 命令间添加延时

    async def _send_data(self, data):
        """
        向LCD发送一个字符数据。
        这是通过4位数据模式分两次发送（高4位和低4位）来实现的。
        这是一个内部辅助方法。

        :param data: 要发送的字符数据。
        :type data: int
        """
        # 发送高4位，确保RS=1（数据模式）
        await self._send_4bits((data & 0xF0) | self.REGISTER_SELECT)
        # 发送低4位
        await self._send_4bits(((data << 4) & 0xF0) | self.REGISTER_SELECT)
        await asyncio.sleep(0.001)  # 数据间添加延时

    async def _init_display(self):
        """执行LCD的初始化序列。"""
        # 等待LCD上电稳定
        await asyncio.sleep(0.05)

        # 初始化序列，按照HD44780规范
        await self._send_command(0x33)  # 初始化到8线模式
        await asyncio.sleep(0.005)
        await self._send_command(0x32)  # 初始化为4线模式
        await asyncio.sleep(0.005)
        await self._send_command(0x28)  # 设置为2行显示, 5x7点阵
        await asyncio.sleep(0.005)
        await self._send_command(0x0C)  # 开启显示, 无光标, 无闪烁
        await asyncio.sleep(0.005)
        await self.clear()  # 清除显示

    def close(self):
        """关闭I2C总线连接。"""
        if self.bus is not None:
            self.bus.close()
            self.bus = None

    def __enter__(self):
        """支持 'with' 语句，返回实例本身。"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """支持 'with' 语句，退出时自动关闭连接。"""
        self.close()

    async def clear(self):
        """清空屏幕并将光标移至左上角（0, 0）。"""
        await self._send_command(self.LCD_CLEARDISPLAY)
        await asyncio.sleep(0.003)  # 清屏命令需要较长时间，增加延时

    async def set_backlight(self, state):
        """
        设置背光开关。

        :param state: True为开启背光, False为关闭背光。
        :type state: bool
        """
        if self.backlight_on != state:
            self.backlight_on = state
            # 重新发送显示控制命令以刷新背光状态
            display_ctrl = self.LCD_DISPLAYCONTROL
            if self.backlight_on:
                display_ctrl |= self.LCD_DISPLAYON
            await self._send_command(display_ctrl)

    async def set_cursor(self, x, y):
        """
        设置光标位置。

        :param x: 列位置 (0-15)。
        :type x: int
        :param y: 行位置 (0-1)。
        :type y: int
        """
        # 限制坐标范围
        x = max(0, min(self.LCD_COLS - 1, x))
        y = max(0, min(self.LCD_ROWS - 1, y))

        # 计算DDRAM地址
        addr = self.LCD_SETDDRAMADDR | (0x40 * y + x)
        await self._send_command(addr)

    async def write(self, x, y, text):
        """
        在指定位置写入字符串。

        :param x: 列位置 (0-15)。
        :type x: int
        :param y: 行位置 (0-1)。
        :type y: int
        :param text: 要显示的字符串。
        :type text: str
        """
        if not isinstance(text, str):
            text = str(text)

        await self.set_cursor(x, y)

        # 逐个字符发送
        for char in text:
            await self._send_data(ord(char))

    async def write_line(self, line, text, align="left"):
        """
        在指定行写入文本，支持对齐方式。

        :param line: 行号 (0-1)。
        :type line: int
        :param text: 要显示的字符串。
        :type text: str
        :param align: 对齐方式 ("left", "center", "right")。
        :type align: str
        """
        if not isinstance(text, str):
            text = str(text)

        # 限制行号范围
        line = max(0, min(self.LCD_ROWS - 1, line))

        # 处理对齐
        if align == "center":
            text = text.center(self.LCD_COLS)
        elif align == "right":
            text = text.rjust(self.LCD_COLS)
        else:  # left
            text = text.ljust(self.LCD_COLS)

        # 截断或填充文本以适应LCD宽度
        text = text[: self.LCD_COLS].ljust(self.LCD_COLS)

        await self.write(0, line, text)

    async def display_data(self, line1=None, line2=None, clear_first=True):
        """
        便捷方法：在两行上显示数据。

        :param line1: 第一行文本。
        :type line1: str
        :param line2: 第二行文本。
        :type line2: str
        :param clear_first: 是否先清屏。
        :type clear_first: bool
        """
        if clear_first:
            await self.clear()

        if line1 is not None:
            await self.write_line(0, line1)

        if line2 is not None:
            await self.write_line(1, line2)


# 异步上下文管理器支持
class AsyncRpiLcd1602(RpiLcd1602):
    """支持异步上下文管理器的LCD1602类"""

    def __init__(
        self,
        address=RpiLcd1602.DEFAULT_ADDRESS,
        backlight_on=True,
        bus_num=1,
        cols=16,
        rows=2,
    ):
        super().__init__(address, backlight_on, bus_num, cols, rows)

    async def __aenter__(self):
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.close()


# 程序入口
async def main():
    """异步主函数示例"""
    try:
        # 使用异步上下文管理器
        async with AsyncRpiLcd1602(
            address=0x27, backlight_on=True, cols=16, rows=2
        ) as lcd:
            await lcd.write(4, 0, "Hello")
            await lcd.write(7, 1, "world!")
            await asyncio.sleep(3)

            await lcd.clear()
            await lcd.write(0, 0, "Testing backlight")
            await asyncio.sleep(1)
            print("Turning backlight off...")
            await lcd.set_backlight(False)
            await asyncio.sleep(2)
            print("Turning backlight on...")
            await lcd.set_backlight(True)
            await lcd.clear()
            await lcd.write(0, 0, "Backlight is ON")
            await asyncio.sleep(2)

            # 测试新的便捷方法
            await lcd.display_data("Async LCD Test", "Centered Text", clear_first=True)
            await asyncio.sleep(3)

            await lcd.display_data("Left aligned", "Right aligned  ", clear_first=True)
            await asyncio.sleep(3)

    except IOError as e:
        print(f"错误: {e}")
    except KeyboardInterrupt:
        print("\n程序被用户中断。")


if __name__ == "__main__":
    asyncio.run(main())
