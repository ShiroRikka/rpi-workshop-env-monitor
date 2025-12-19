from pydantic_settings import BaseSettings
import board


class Settings(BaseSettings):
    """
    应用配置类。
    Pydantic 会自动从环境变量中读取同名配置，如果找不到则使用默认值。
    """

    # --- API 配置 ---
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    # --- 数据采集配置 ---
    # 传感器数据采集间隔（秒）
    DATA_COLLECTION_INTERVAL: int = 3

    # LCD屏幕刷新间隔（秒）
    DISPLAY_UPDATE_INTERVAL: int = 3

    # --- 硬件引脚配置 ---
    # 使用 BCM 编码
    DHT11_PIN: board.pin = board.D24
    FAN_RELAY_PIN: int = 25
    # 假设烟雾传感器连接到MCP3008的0号通道
    SMOKE_SENSOR_ADC_CHANNEL: int = 0

    # --- 控制逻辑阈值 ---
    # 烟雾浓度超过此值时触发风扇
    SMOKE_THRESHOLD: float = 600.0
    TEMPERATURE_THRESHOLD: float = 22
    # --- 数据库配置 ---
    # 数据库文件的路径
    DATABASE_URL: str = "./data.db"

    # --- 日志配置 ---
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "app.log"

    class Config:
        # Pydantic 会自动加载项目根目录下的 .env 文件
        env_file = ".env"
        env_file_encoding = "utf-8"


# 创建一个全局的 settings 对象，其他模块直接导入这个对象即可
settings = Settings()
