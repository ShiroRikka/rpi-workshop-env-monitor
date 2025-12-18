import asyncio
from hardware.dht11_sensor import DHT11Sensor
from hardware.mock_sensors import MockSmokeSensor, MockADCSensor
# 未来，你只需要把下面的 import 换成真实的
# from hardware.smoke_sensor import RealSmokeSensor
# from hardware.adc_sensor import RealADCSensor


class DataManager:
    def __init__(self, config, shared_state: dict):
        self.config = config
        self.shared_state = shared_state
        self.sensors = self._initialize_sensors()
        # ... 其他初始化 ...

    def _initialize_sensors(self):
        """工厂方法：根据配置创建传感器实例"""
        sensors = {}

        # DHT11 是真实的，所以我们创建真实的实例
        import board

        sensors["dht11"] = DHT11Sensor(pin=board.D24)  # 假设接在GPIO24

        # 其他传感器还没到，我们创建模拟实例
        sensors["smoke"] = MockSmokeSensor(pin=0)
        sensors["adc"] = MockADCSensor(pin=0)

        return sensors

    async def run(self):
        """主循环，持续采集数据"""
        print("DataManager: 开始数据采集循环...")
        while True:
            try:
                # 并发读取所有传感器（无论是真是假）
                readings = await asyncio.gather(
                    self.sensors["dht11"].read(), self.sensors["smoke"].read(), self.sensors["adc"].read()
                )

                dht11_data, smoke_level, adc_value = readings

                # 更新共享状态
                self.shared_state.update(
                    {
                        "temperature": dht11_data["temperature"],
                        "humidity": dht11_data["humidity"],
                        "smoke_level": smoke_level,
                        "adc_value": adc_value,
                    }
                )

                print(f"采集到数据: {self.shared_state}")

                # ... 执行控制逻辑、存数据库等 ...

            except Exception as e:
                print(f"数据采集中发生错误: {e}")

            await asyncio.sleep(self.config.DATA_COLLECTION_INTERVAL)
