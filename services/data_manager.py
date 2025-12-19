import asyncio
from loguru import logger
from hardware.dht11_sensor import DHT11Sensor
from hardware.mock_sensors import MockSmokeSensor, MockADCSensor
from hardware.actuators import Relay
from .base_manager import BaseManager
# 未来，你只需要把下面的 import 换成真实的
# from hardware.smoke_sensor import RealSmokeSensor
# from hardware.adc_sensor import RealADCSensor


class DataManager(BaseManager):
    def __init__(self, config, shared_state: dict):
        super().__init__(config, shared_state)
        self.sensors = self._initialize_sensors()
        self.actuators = self._initialize_actuators()
        # ... 其他初始化 ...

    def _initialize_sensors(self):
        """工厂方法：根据配置创建传感器实例"""
        sensors = {}
        sensors["dht11"] = DHT11Sensor(pin=self.config.DHT11_PIN)  # 假设接在GPIO24

        # 其他传感器还没到，我们创建模拟实例
        sensors["smoke"] = MockSmokeSensor(pin=0)
        sensors["adc"] = MockADCSensor(pin=0)
        return sensors

    def _initialize_actuators(self):
        actuators = {}
        fan_relay = Relay(self.config.FAN_RELAY_PIN)
        actuators["fan"] = fan_relay
        return actuators

    async def run(self):
        """主循环，持续采集数据"""
        logger.info("DataManager: 开始数据采集与控制循环...")
        while True:
            try:
                # 并发读取所有传感器
                dht11_data, smoke_level, adc_value = await asyncio.gather(
                    self.sensors["dht11"].read(),
                    self.sensors["smoke"].read(),
                    self.sensors["adc"].read(),
                )

                # 更新共享状态
                self.shared_state.update(
                    {
                        "temperature": dht11_data["temperature"],
                        "humidity": dht11_data["humidity"],
                        "smoke_level": smoke_level,
                        "adc_value": adc_value,
                    }
                )

                # 执行控制逻辑
                fan = self.actuators["fan"]
                if self.shared_state["temperature"] > self.config.TEMPERATURE_THRESHOLD:
                    if not fan._is_on:
                        await fan.turn_on()
                else:
                    if fan._is_on:
                        await fan.turn_off()

                # 更新共享状态
                self.shared_state["fan_on"] = fan._is_on

                logger.info(
                    f"采集到数据: T={dht11_data['temperature']:.1f}°C,H={dht11_data['humidity']:.1f}%, S={smoke_level:.2f}, 风扇状态: {'开启' if fan._is_on else '关闭'}"
                )

                # ... 执行控制逻辑、存数据库等 ...

            except Exception as e:
                logger.error(f"数据采集中发生错误: {e}")

            await asyncio.sleep(self.config.DATA_COLLECTION_INTERVAL)
