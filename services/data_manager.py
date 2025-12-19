import asyncio
from loguru import logger
from hardware.dht11_sensor import DHT11Sensor
from hardware.mock_sensors import MockSmokeSensor
from hardware.actuators import Relay
from database.db import Database
from .base_manager import BaseManager
# 未来，你只需要把下面的 import 换成真实的
# from hardware.smoke_sensor import RealSmokeSensor
# from hardware.adc_sensor import RealADCSensor


class DataManager(BaseManager):
    def __init__(self, config, shared_state):
        super().__init__(config, shared_state)
        self.sensors = self._initialize_sensors()
        self.actuators = self._initialize_actuators()
        self.db = Database(self.config.DATABASE_URL)
        # ... 其他初始化 ...

    def _initialize_sensors(self):
        """工厂方法：根据配置创建传感器实例"""
        return {
            "dht11": DHT11Sensor(pin=self.config.DHT11_PIN),
            "smoke": MockSmokeSensor(pin=0),
            # 注意：代码中引用了 "adc" 传感器但未初始化，需要添加
            # "adc": ADCSensor(pin=self.config.SMOKE_SENSOR_ADC_CHANNEL)
        }

    def _initialize_actuators(self):
        """工厂方法：根据配置创建执行器实例"""
        return {"fan": Relay(self.config.FAN_RELAY_PIN)}

    async def run(self):
        """主循环，持续采集数据"""
        logger.info("DataManager: 开始数据采集与控制循环...")
        while True:
            try:
                # 并发读取所有传感器
                # 注意：暂时注释掉 adc 传感器，因为未初始化
                dht11_data, smoke_level = await asyncio.gather(
                    self.sensors["dht11"].read(),
                    self.sensors["smoke"].read(),
                    # self.sensors["adc"].read(),
                )

                # 执行控制逻辑
                await self._control_fan(dht11_data["temperature"])

                # 更新共享状态
                self.shared_state.update(
                    {
                        "temperature": dht11_data["temperature"],
                        "humidity": dht11_data["humidity"],
                        "smoke_level": smoke_level,
                        "fan_on": self.actuators["fan"]._is_on,
                    }
                )

                # 保存数据到数据库
                await self._save_sensor_data(dht11_data, smoke_level)

                logger.info(
                    f"采集到数据: T={dht11_data['temperature']:.1f}°C,"
                    f"H={dht11_data['humidity']:.1f}%, "
                    f"S={smoke_level:.2f}, "
                    f"风扇状态: {'开启' if self.actuators['fan']._is_on else '关闭'}"
                )

            except Exception as e:
                logger.error(f"数据采集中发生错误: {e}")

            await asyncio.sleep(self.config.DATA_COLLECTION_INTERVAL)

    async def _control_fan(self, temperature: float):
        """根据温度控制风扇"""
        fan = self.actuators["fan"]

        # 温度超过阈值且风扇未开启，则开启风扇
        if temperature > self.config.TEMPERATURE_THRESHOLD and not fan._is_on:
            await fan.turn_on()
            logger.info(
                f"温度 {temperature:.1f}°C 超过阈值 {self.config.TEMPERATURE_THRESHOLD}°C，风扇已开启"
            )
        # 温度低于阈值且风扇已开启，则关闭风扇
        elif temperature <= self.config.TEMPERATURE_THRESHOLD and fan._is_on:
            await fan.turn_off()
            logger.info(
                f"温度 {temperature:.1f}°C 低于阈值 {self.config.TEMPERATURE_THRESHOLD}°C，风扇已关闭"
            )

    async def _save_sensor_data(self, dht11_data: dict, smoke_level: float):
        """保存传感器数据到数据库"""
        try:
            await self.db.insert_reading(
                temperature=dht11_data["temperature"],
                humidity=dht11_data["humidity"],
                smoke_level=smoke_level,
                fan_on=self.actuators["fan"]._is_on,
            )
        except Exception as e:
            logger.error(f"保存传感器数据到数据库失败: {e}")
            # 不重新抛出异常，避免中断数据采集循环
