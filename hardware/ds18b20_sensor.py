"""
DS18B20温度传感器驱动

使用前提：
1. 确保内核模块已加载：
   sudo modprobe w1-gpio
   sudo modprobe w1-therm

2. 找到设备ID：
   cd /sys/bus/w1/devices
   ls
   # 找到类似 "28-xxxxxxxxxxxx" 的设备ID

3. 读取温度数据：
   cat <设备ID>/w1_slave
"""

import subprocess
from pathlib import Path

from .base_sensor import BaseSensor


class DS18B20Sensor(BaseSensor):
    """DS18B20数字温度传感器驱动类

    继承自BaseSensor，但DS18B20是1-Wire设备，不需要GPIO引脚参数。
    通过读取/sys/bus/w1/devices/下的设备文件获取温度数据。
    """

    def __init__(self, device_id: str | None = None, pin: int = 0):
        """初始化DS18B20传感器

        Args:
            device_id: DS18B20设备的唯一ID，如"28-xxxxxxxxxxxx"。如果为None，将尝试自动检测。
            pin: 占位参数，保持与基类兼容，DS18B20不使用GPIO引脚
        """
        super().__init__(pin)

        # 加载必要的内核模块
        self._load_kernel_modules()

        # 设置或自动检测设备ID
        self._device_id = device_id or self._auto_detect_device()
        if not self._device_id:
            raise ValueError("无法找到DS18B20设备，请检查硬件连接和内核模块")

        self._device_path = Path(f"/sys/bus/w1/devices/{self._device_id}/w1_slave")

    def _load_kernel_modules(self) -> None:
        """加载1-Wire内核模块"""
        subprocess.run(["modprobe", "w1-gpio"], check=True, capture_output=True)
        subprocess.run(["modprobe", "w1-therm"], check=True, capture_output=True)

    def _auto_detect_device(self) -> str | None:
        """自动检测第一个可用的DS18B20设备

        Returns:
            设备ID字符串，如果未找到则返回None
        """
        devices_path = Path("/sys/bus/w1/devices")
        if not devices_path.exists():
            return None

        # 查找以"28-"开头的目录（DS18B20设备ID格式）
        for device_dir in devices_path.iterdir():
            if device_dir.is_dir() and device_dir.name.startswith("28-"):
                return device_dir.name
        return None

    async def read(self) -> dict[str, float] | None:
        """读取温度值

        Returns:
            摄氏温度值，如果读取失败则返回None
        """
        try:
            with open(self._device_path, "r") as f:
                data = f.read()

            # 解析温度数据
            lines = data.strip().split("\n")
            if len(lines) < 2:
                return None

            # 检查第一行是否包含"YES"，表示数据有效
            if "YES" not in lines[0]:
                return None

            # 从第二行提取温度值
            temp_parts = lines[1].split(" ")
            if len(temp_parts) < 10 or not temp_parts[9].startswith("t="):
                return None

            # 转换温度值
            temp_raw = temp_parts[9][2:]  # 去掉"t="前缀
            temperature = float(temp_raw) / 1000.0
            self._value = {"temperature": temperature}
            return self._value

        except Exception:
            return None
