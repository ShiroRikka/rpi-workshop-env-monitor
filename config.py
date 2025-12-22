from pydantic_settings import BaseSettings
import board


class Settings(BaseSettings):
    """应用配置类。

    Pydantic 会自动从环境变量中读取同名配置，如果找不到则使用默认值。
    """

    # API 配置
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    # 数据采集配置（秒）
    DATA_COLLECTION_INTERVAL: int = 3
    DISPLAY_UPDATE_INTERVAL: int = 3

    # 硬件引脚配置
    DHT11_PIN: board.pin = board.D24
    FAN_RELAY_PIN: int = 25
    SMOKE_SENSOR_ADC_CHANNEL: int = 0
    DHT11_MODE: str = "humid"  # 'temp' 或 'humid'
    DS18B20_DEVICE_ID: str | None = None

    # 控制逻辑阈值
    SMOKE_THRESHOLD: float = 600.0
    TEMPERATURE_THRESHOLD: float = 22.0

    # 数据库配置
    DATABASE_URL: str = "./data.db"

    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "app.log"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


# 全局配置实例
settings = Settings()
