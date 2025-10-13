import pymysql
from pymysql import MySQLError
from loguru import logger
from tenacity import retry, stop_after_attempt
from dotenv import load_dotenv
import os


class DatabaseManager:
    """
    一个用于管理MySQL数据库连接、初始化数据库结构及插入环境数据的类。

    该类封装了与MySQL数据库的交互，提供了重试机制、清晰的错误处理和灵活的配置选项。
    """

    def __init__(
        self,
        host: str,
        port: int,
        user: str,
        password: str,
        database_name: str = "rpi_env_monitor",
        table_name: str = "environment_data",
    ):
        """
        初始化数据库管理器。

        :param host: MySQL主机地址
        :type host: str
        :param port: MySQL端口
        :type port: int
        :param user: MySQL用户名
        :type user: str
        :param password: MySQL密码
        :type password: str
        :param database_name: 要使用的数据库名称，默认为 'rpi_env_monitor'
        :type database_name: str
        :param table_name: 要使用的数据表名称，默认为 'environment_data'
        :type table_name: str
        """
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database_name = database_name
        self.table_name = table_name

    @retry(stop=stop_after_attempt(3))
    def _get_connection(self, database: str | None = None):
        """
        获取数据库连接，带有重试机制。

        :param database: 指定连接的数据库，若为None则不指定数据库
        :type database: str | None
        :return: 数据库连接对象
        :rtype: pymysql.connections.Connection
        """
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

    def initialize(self):
        """
        初始化数据库和数据表。

        此方法会创建数据库（如果不存在）和数据表（如果不存在）。
        在执行数据操作前，应显式调用此方法。
        """
        logger.info(
            f"正在初始化数据库环境: 数据库 '{self.database_name}', 表 '{self.table_name}'..."
        )
        try:
            # 创建数据库
            with self._get_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        f"CREATE DATABASE IF NOT EXISTS `{self.database_name}`"
                    )

            # 创建数据表
            with self._get_connection(self.database_name) as connection:
                with connection.cursor() as cursor:
                    create_table_sql = f"""
                        CREATE TABLE IF NOT EXISTS `{self.table_name}` (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                            temperature FLOAT,
                            humidity FLOAT,
                            ppm FLOAT
                        )
                    """
                    cursor.execute(create_table_sql)
            logger.success("数据库初始化成功")
        except MySQLError as e:
            logger.error(f"数据库初始化失败: {e}")
            raise

    def insert_env_data(
        self,
        temp: float | int | None = None,
        humid: float | int | None = None,
        ppm: float | None = None,
    ):
        """
        将环境数据（温度、湿度和烟雾浓度）插入到数据表中。
        如果某个参数为 None，则该字段在数据库中将被记为 NULL。

        :param temp: 温度值，默认为 None
        :type temp: float | int | None
        :param humid: 湿度值，默认为 None
        :type humid: float | int | None
        :param ppm: 烟雾浓度值，默认为 None
        :type ppm: float | None
        :raises MySQLError: 当数据库操作失败时
        """
        try:
            with self._get_connection(self.database_name) as connection:
                with connection.cursor() as cursor:
                    sql = f"""
                        INSERT INTO `{self.table_name}` (temperature, humidity, ppm) VALUES (%s, %s, %s)
                    """
                    cursor.execute(sql, (temp, humid, ppm))
                    logger.info(f"成功插入数据: 温度={temp}, 湿度={humid}, ppm={ppm}")
        except MySQLError as e:
            logger.error(f"MySQL 错误: 数据插入失败 - {e}")
            raise
        except Exception as e:
            logger.exception(f"未知错误导致插入失败: {e}")
            raise


if __name__ == "__main__":
    # 配置数据库连接参数
    # 加载环境变量
    load_dotenv()

    # 数据库配置
    DB_CONFIG = {
        "host": os.getenv("DB_HOST"),
        "port": int(os.getenv("DB_PORT", 3306)),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
    }

    try:
        # 创建数据库管理器实例
        db_manager = DatabaseManager(**DB_CONFIG)

        # 显式初始化数据库和表
        db_manager.initialize()

        # 插入完整数据
        db_manager.insert_env_data(temp=23.5, humid=45, ppm=120)

        # 插入部分数据，ppm将为NULL
        db_manager.insert_env_data(temp=24.1, humid=44.2)

        # 只插入温度，其他为NULL
        db_manager.insert_env_data(temp=25.0)

        # 测试不传入任何数据，所有字段均为NULL
        db_manager.insert_env_data()

    except ValueError as e:
        logger.error(f"数据输入错误: {e}")
    except MySQLError as e:
        logger.error(f"数据库操作失败，请检查配置和服务状态: {e}")
    except Exception as e:
        logger.exception(f"发生未知错误: {e}")
