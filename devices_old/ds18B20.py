import os


class DS18B20:
    """DS18B20温度传感器模块驱动"""

    def __init__(self):
        """初始化DS18B20传感器"""
        self.device = ""
        for i in os.listdir("/sys/bus/w1/devices"):
            if i != "w1_bus_master1":
                self.device = i

    def read_temperature(self) -> float:
        """从DS18B20获取温度

        :return: 温度
        :rtype: float
        """
        location = f"/sys/bus/w1/devices/{self.device}/w1_slave"
        with open(location) as temperature_file:
            raw_data = temperature_file.read()
        secondline = raw_data.split("\n")[1]
        temperature_data = secondline.split(" ")[9]
        temperature = float(temperature_data[2:])
        temperature /= 1000
        return temperature


if __name__ == "__main__":
    sensor = DS18B20()
    try:
        while True:
            print(f"Current temperature : {sensor.read_temperature():0.3f}℃")
    except KeyboardInterrupt:
        pass
