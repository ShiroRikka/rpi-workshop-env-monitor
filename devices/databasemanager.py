import pymysql
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_fixed


class DatabaseManager:
    def __init__(self, host: str, port: int, user: str, password: str = ""):
        """
        数据库管理器类
        :param host: MySQL主机地址
        :param port: MySQL端口
        :param user: MySQL用户名
        :param password: MySQL密码
        """
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self._init_database()

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def _get_connection(self, database=None):
        return pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=database,
            connect_timeout=5,
            read_timeout=5,
            write_timeout=5,
            autocommit=True,
            init_command="SET time_zone = '+08:00'",
        )

    def _init_database(self):
        logger.info("正在初始化数据库环境...")
        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("CREATE DATABASE IF NOT EXISTS rpi_env_monitor")

        with self._get_connection("rpi_env_monitor") as connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS environment_data (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        temperature FLOAT NOT NULL,
                        humidity FLOAT NOT NULL
                    )
                """)
        logger.success("数据库初始化成功")

    def insert_env_data(self, temp: int | float | None, humid: float | int | None):
        """
        将传入数据存入数据库中
        :param temp: 温度
        :param humid: 湿度
        """
        with self._get_connection("rpi_env_monitor") as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO environment_data (temperature, humidity) VALUES (%s, %s)
                """,
                    (temp, humid),
                )


if __name__ == "__main__":
    db = DatabaseManager("127.0.0.1", 3306, "admin", "123456")
    db.insert_env_data(23.5, 45)
