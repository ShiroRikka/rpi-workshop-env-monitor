from pydantic_settings import BaseSettings
import board
import sys


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

    # LCD显示器配置
    LCD_ADDRESS: int = 0x27  # I2C地址
    LCD_BUS_NUM: int = 1  # I2C总线编号
    LCD_COLS: int = 16  # LCD列数
    LCD_ROWS: int = 2  # LCD行数

    # 硬件引脚配置
    DHT11_PIN: board.pin = board.D24  # DHT11需要board.pin对象
    FAN_RELAY_PIN: int = 25
    SMOKE_SENSOR_ADC_CHANNEL: int = 0
    DHT11_MODE: str = "humid"  # 'temp' 或 'humid'
    DS18B20_DEVICE_ID: str | None = None
    MQ2_CHANNLE: int = 0
    FAN_MOTOR_FORWARD: int = 17
    FAN_MOTOR_BACKWARD: int = 18
    FAN_MOTOR_ENABLE: int = 19
    WARNING_PIN: int = 22  # gpiozero使用BCM引脚号

    # 控制逻辑阈值
    SMOKE_THRESHOLD: float = 600.0
    TEMPERATURE_THRESHOLD: float = 22.0

    # 风扇变速控制参数
    FAN_MIN_TEMP: float = 20.0  # 风扇开始转动的最低温度
    FAN_MAX_TEMP: float = 35.0  # 风扇全速运行的最高温度
    FAN_MIN_SPEED: float = 0.1  # 最低转速比例 (0.0-1.0)
    FAN_MAX_SPEED: float = 1.0  # 最高转速比例 (0.0-1.0)

    # 数据库配置
    DATABASE_URL: str = "./data.db"

    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_PATH: any = sys.stderr

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


# 全局配置实例
settings = Settings()
