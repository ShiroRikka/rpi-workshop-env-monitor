import pymysql
from loguru import logger


class EnvironmentDatabaseManager:
    def __init__(self, host: str, user: str, password: str = ""):
        self.host = host
        self.user = user
        self.password = password
        self.database_name = "rpi_env_monitor"
        self.table_name = "environment_data"
        self._create_database()
        self._create_table()
        logger.success("数据库初始化完成")

    def _connect(self):
        return pymysql.connect(host=self.host, user=self.user, password=self.password)

    def _create_database(self):
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database_name}")
        logger.success(f"创建数据库 {self.database_name} 成功")

    def _connect_to_db(self):
        return pymysql.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database_name,
        )

    def _create_table(self):
        with self._connect_to_db() as connection:
            with connection.cursor() as cursor:
                cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS {self.table_name} (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        temperature FLOAT NOT NULL,
                        humidity FLOAT NOT NULL
                    )
                """)
        logger.success(f"创建表 {self.table_name} 成功")

    def insert_env_data(self, temp: float, humid: float | int):
        """
        将传入数据存入数据库中
        :param temp: 温度
        :param humid: 湿度
        :return: None
        """
        with self._connect_to_db() as connection:
            with connection.cursor() as cursor:
                cursor.execute(f"""
                    INSERT INTO {self.table_name} (temperature, humidity) VALUES ({temp}, {humid})
                """)


if __name__ == "__main__":
    EDM = EnvironmentDatabaseManager("127.0.0.1", "admin", "123456")
    EDM.insert_env_data(23.5, 45)
    pass
