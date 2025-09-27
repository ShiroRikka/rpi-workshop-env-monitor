import time

import smbus


class LCD1602:
    """LCD1602模块驱动"""

    def __init__(self, addr=0x27, bl: int = 1):
        """初始化LCD1602

        :param addr: I2C地址,默认为0x27
        :param bl: 背光,1为开,0为关,默认为1
        :type bl: bool
        """
        self.bus = smbus.SMBus(1)
        self.addr = addr
        self.bl = bl
        self._init_lcd()

    def _write_word(self, data):
        temp = data
        temp |= 0x08 if self.bl == 1 else temp & 0xF7
        self.bus.write_byte(self.addr, temp)

    def _send_command(self, comm):
        lcd_buf = comm & 0xF0
        lcd_buf |= 0x04
        self._write_word(lcd_buf)
        time.sleep(0.002)
        lcd_buf &= 0xFB
        self._write_word(lcd_buf)

        lcd_buf = (comm & 0x0F) << 4
        lcd_buf |= 0x04
        self._write_word(lcd_buf)
        time.sleep(0.002)
        lcd_buf &= 0xFB
        self._write_word(lcd_buf)

    def _init_lcd(self):
        try:
            self._send_command(0x33)
            time.sleep(0.005)
            self._send_command(0x32)
            time.sleep(0.005)
            self._send_command(0x28)
            time.sleep(0.005)
            self._send_command(0x0C)
            time.sleep(0.005)
            self._send_command(0x01)
            self.bus.write_byte(self.addr, 0x08)
        except:
            return False
        else:
            return True

    def _send_data(self, data):
        lcd_buf = data & 0xF0
        lcd_buf |= 0x05
        self._write_word(lcd_buf)
        time.sleep(0.002)
        lcd_buf &= 0xFB
        self._write_word(lcd_buf)

        lcd_buf = (data & 0x0F) << 4
        lcd_buf |= 0x05
        self._write_word(lcd_buf)
        time.sleep(0.002)
        lcd_buf &= 0xFB
        self._write_word(lcd_buf)

    def display(self, lcd_x: int, lcd_y: int, lcd_str: str):
        """在LCD1602指定位置显示字符串

        :param lcd_x: 列位置,范围0-15
        :type lcd_x: int
        :param lcd_y: 行位置,范围0-1
        :type lcd_y: int
        :param lcd_str: 要显示的字符串
        :type lcd_str: str
        """
        lcd_x = 0 if lcd_x < 0 else lcd_x
        lcd_x = 15 if lcd_x > 15 else lcd_x
        lcd_y = 0 if lcd_y < 0 else lcd_y
        lcd_y = 1 if lcd_y > 1 else lcd_y

        self._send_command(0x80 + 0x40 * lcd_y + lcd_x)
        for char in lcd_str:
            self._send_data(ord(char))


if __name__ == "__main__":
    lcd = LCD1602(addr=0x27, bl=1)
    lcd.display(0, 0, "Hello!!!")
    lcd.display(0, 1, "I am ShiroRikka")
    time.sleep(2)
