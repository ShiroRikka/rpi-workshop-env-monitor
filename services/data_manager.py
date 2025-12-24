import asyncio
from loguru import logger

# 导入传感器类
from hardware.dht11_sensor import DHT11Sensor
from hardware.ds18b20_sensor import DS18B20Sensor
from hardware.mq2_sensor import MQ2Sensor

# 导入执行器类
from hardware.actuators import RpiMotor

# 导入其他类
from database.db import Database
from .base_manager import BaseManager


class DataManager(BaseManager):
    def __init__(self, config, shared_state):
        super().__init__(config, shared_state)
        self.sensors = self._initialize_sensors()
        self.actuators = self._initialize_actuators()
        self.db = Database(self._config.DATABASE_URL)

    async def run(self):
        """主循环，持续采集数据"""
        logger.info("DataManager: 开始数据采集与控制循环...")
        while True:
            try:
                # 并发读取所有传感器
                dht11_data, ds18b20_data, mq2_data = await asyncio.gather(
                    self.sensors["dht11"].read(),
                    self.sensors["ds18b20"].read(),
                    self.sensors["mq2"].read(),
                )

                # 执行控制逻辑
                await self._control_fan(ds18b20_data)

                # 更新共享状态
                self._shared_state.update(
                    {
                        "temperature": ds18b20_data,
                        "humidity": dht11_data,
                        "smoke_level": mq2_data,
                        "fan_on": self.actuators["fan"]._is_on,
                    }
                )

                # 保存数据到数据库
                await self._save_sensor_data(
                    temp=ds18b20_data,
                    humidity=dht11_data,
                    smoke_level=mq2_data,
                    fan_on=self.actuators["fan"]._is_on,
                )

                logger.info(
                    f"采集到数据: T={ds18b20_data:.1f}°C,"
                    f"H={dht11_data:.1f}%, "
                    f"烟雾={mq2_data:.2f}, "
                    f"风扇状态: {'开启' if self.actuators['fan']._is_on else '关闭'}"
                )

            except Exception as e:
                logger.error(f"数据采集中发生错误: {e}")

            await asyncio.sleep(self._config.DATA_COLLECTION_INTERVAL)

    def _initialize_sensors(self):
        """工厂方法：根据配置创建传感器实例"""
        return {
            "dht11": DHT11Sensor(
                pin=self._config.DHT11_PIN, mode=self._config.DHT11_MODE
            ),
            "ds18b20": DS18B20Sensor(device_id=self._config.DS18B20_DEVICE_ID),
            "mq2": MQ2Sensor(channle=self._config.MQ2_CHANNLE),
        }

    def _initialize_actuators(self):
        """工厂方法：根据配置创建执行器实例"""
        return {
            "fan": RpiMotor(
                self._config.FAN_MOTOR_FORWARD,
                self._config.FAN_MOTOR_BACKWARD,
                self._config.FAN_MOTOR_ENABLE,
            )
        }

    async def _control_fan(self, temperature: float):
        """根据温度控制风扇"""
        fan = self.actuators["fan"]

        # 温度超过阈值且风扇未开启，则开启风扇
        if temperature > self._config.TEMPERATURE_THRESHOLD and not fan._is_on:
            await fan.turn_on()
            logger.info(
                f"温度 {temperature:.1f}°C 超过阈值 {self._config.TEMPERATURE_THRESHOLD}°C，风扇已开启"
            )
        # 温度低于阈值且风扇已开启，则关闭风扇
        elif temperature <= self._config.TEMPERATURE_THRESHOLD and fan._is_on:
            await fan.turn_off()
            logger.info(
                f"温度 {temperature:.1f}°C 低于阈值 {self._config.TEMPERATURE_THRESHOLD}°C，风扇已关闭"
            )

    async def _save_sensor_data(
        self,
        temp: float = None,
        humidity: float = None,
        smoke_level: float = None,
        fan_on: bool = False,
    ):
        """保存传感器数据到数据库"""
        try:
            await self.db.insert_reading(
                temperature=temp,
                humidity=humidity,
                smoke_level=smoke_level,
                fan_on=fan_on,
            )
        except Exception as e:
            logger.error(f"保存传感器数据到数据库失败: {e}")
            # 不重新抛出异常，避免中断数据采集循环
