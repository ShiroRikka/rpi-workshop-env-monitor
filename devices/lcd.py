import time
import smbus

class RpiLcd1602:
    """
    用于通过I2C接口控制LCD1602显示器的类。
    该类封装了与基于PCF8574 I/O扩展器的I2C LCD模块进行通信所需的所有功能。
    """
    # I2C设备默认地址
    DEFAULT_ADDRESS = 0x27

    def __init__(self, address=DEFAULT_ADDRESS, backlight_on=True, bus_num=1):
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
        self.bus = smbus.SMBus(bus_num)
        self.backlight_on = backlight_on
      
        try:
            self._init_display()
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
            data |= 0x08  # 设置背光开启位
        else:
            data &= 0xF7  # 设置背光关闭位
        self.bus.write_byte(self.addr, data)

    def _send_command(self, comm):
        """
        向LCD发送一个命令。
        这是通过4位数据模式分两次发送（高4位和低4位）来实现的。
        这是一个内部辅助方法。

        :param comm: 要发送的命令字节。
        :type comm: int
        """
        # 发送高4位
        buf = comm & 0xF0
        buf |= 0x04  # RS=0, RW=0, EN=1
        self._write_word(buf)
        time.sleep(0.002)
        buf &= 0xFB  # EN=0
        self._write_word(buf)

        # 发送低4位
        buf = (comm & 0x0F) << 4
        buf |= 0x04  # RS=0, RW=0, EN=1
        self._write_word(buf)
        time.sleep(0.002)
        buf &= 0xFB  # EN=0
        self._write_word(buf)

    def _send_data(self, data):
        """
        向LCD发送一个字符数据。
        这是通过4位数据模式分两次发送（高4位和低4位）来实现的。
        这是一个内部辅助方法。

        :param data: 要发送的字符数据。
        :type data: int
        """
        # 发送高4位
        buf = data & 0xF0
        buf |= 0x05  # RS=1, RW=0, EN=1
        self._write_word(buf)
        time.sleep(0.002)
        buf &= 0xFB  # EN=0
        self._write_word(buf)

        # 发送低4位
        buf = (data & 0x0F) << 4
        buf |= 0x05  # RS=1, RW=0, EN=1
        self._write_word(buf)
        time.sleep(0.002)
        buf &= 0xFB  # EN=0
        self._write_word(buf)

    def _init_display(self):
        """执行LCD的初始化序列。"""
        self._send_command(0x33)  # 初始化到8线模式
        time.sleep(0.005)
        self._send_command(0x32)  # 初始化为4线模式
        time.sleep(0.005)
        self._send_command(0x28)  # 设置为2行显示, 5x7点阵
        time.sleep(0.005)
        self._send_command(0x0C)  # 开启显示, 无光标, 无闪烁
        time.sleep(0.005)
        self.clear()              # 清除显示

    def close(self):
        """关闭I2C总线连接。"""
        if hasattr(self, 'bus'):
            self.bus.close()

    def __enter__(self):
        """支持 'with' 语句，返回实例本身。"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """支持 'with' 语句，退出时自动关闭连接。"""
        self.close()

    def clear(self):
        """清空屏幕并将光标移至左上角（0, 0）。"""
        self._send_command(0x01)
        time.sleep(0.002) # 清屏命令需要较长时间

    def set_backlight(self, state):
        """
        设置背光开关。

        :param state: True为开启背光, False为关闭背光。
        :type state: bool
        """
        if self.backlight_on != state:
            self.backlight_on = state
            # 重新发送显示控制命令以刷新背光状态
            display_ctrl = 0x08  # Display off, Cursor off, Blink off
            if self.backlight_on:
                display_ctrl |= 0x04  # Display on
            self._send_command(display_ctrl)
          
    def write(self, x, y, text):
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

        # 限制坐标范围
        x = max(0, min(15, x))
        y = max(0, min(1, y))

        # 计算DDRAM地址
        addr = 0x80 + 0x40 * y + x
        self._send_command(addr)

        # 逐个字符发送
        for char in text:
            self._send_data(ord(char))

# 程序入口
if __name__ == '__main__':
    try:
        # 使用 'with' 语句可以确保I2C总线被正确关闭
        with LCD1602(address=0x27, backlight_on=True) as lcd:
            lcd.write(4, 0, 'Hello')
            lcd.write(7, 1, 'world!')
            time.sleep(3)
          
            lcd.clear()
            lcd.write(0, 0, "Testing backlight")
            time.sleep(1)
            print("Turning backlight off...")
            lcd.set_backlight(False)
            time.sleep(2)
            print("Turning backlight on...")
            lcd.set_backlight(True)
            lcd.clear()
            lcd.write(0, 0, "Backlight is ON")
            time.sleep(2)
          
    except IOError as e:
        print(f"错误: {e}")
    except KeyboardInterrupt:
        print("\n程序被用户中断。")