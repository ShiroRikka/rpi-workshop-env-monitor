import smbus


class PCF8591:
    """PCF8591 模拟量输入输出模块驱动"""

    def __init__(self, addr=0x48):
        """
        :param addr: I2C 地址,默认地址为0x48
        :type addr: int
        """
        self.bus = smbus.SMBus(1)
        self.addr = addr

    def read(self, chn):  # 通道选择，范围是0-3之间
        try:
            self.bus.write_byte(self.addr, 0x40) if chn == 0 else None
            self.bus.write_byte(self.addr, 0x41) if chn == 1 else None
            self.bus.write_byte(self.addr, 0x42) if chn == 2 else None
            self.bus.write_byte(self.addr, 0x43) if chn == 3 else None
            self.bus.read_byte(self.addr)  # 开始进行读取转换
        except Exception as e:
            print(f"Address: {self.addr}: {e}")
        return self.bus.read_byte(self.addr)

    def write(self, val):
        try:
            temp = int(val)
            self.bus.write_byte_data(self.addr, 0x40, temp)
        except Exception as e:
            print(f"Error: Device address: 0x{self.addr:02X}: {e}")


if __name__ == "__main__":
    adc = PCF8591(0x48)
    while True:
        print("AIN0 = ", adc.read(0))
        print("AIN1 = ", adc.read(1))
        tmp = adc.read(0) * (255 - 125) / 255 + 125
        adc.write(tmp)
