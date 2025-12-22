import aiosqlite
from datetime import datetime
from typing import List, Dict, Any


class Database:
    """异步数据库操作封装类"""

    def __init__(self, db_url: str):
        self.db_url = db_url
        self.conn: aiosqlite.Connection

    async def connect(self):
        """建立数据库连接"""
        self.conn = await aiosqlite.connect(self.db_url)
        # 启用外键约束
        await self.conn.execute("PRAGMA foreign_keys = ON")
        print("数据库连接已建立。")

    async def disconnect(self):
        """关闭数据库连接"""
        if self.conn:
            await self.conn.close()
            print("数据库连接已关闭。")

    async def _create_tables(self):
        """创建数据表（如果不存在）"""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS sensor_readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME NOT NULL,
            temperature REAL,
            humidity REAL,
            smoke_level REAL,
            fan_on BOOLEAN
        );
        """
        await self.conn.execute(create_table_sql)
        await self.conn.commit()
        print("数据表检查/创建完成。")

    async def initialize(self):
        """初始化数据库：连接并创建表"""
        await self.connect()
        await self._create_tables()

    async def insert_reading(
        self,
        temperature: float = None,
        humidity: float = None,
        smoke_level: float = None,
        fan_on: bool = False,
    ):
        """插入一条新的传感器读数"""
        if not self.conn:
            raise RuntimeError("数据库未连接！")

        sql = """
        INSERT INTO sensor_readings (timestamp, temperature, humidity, smoke_level, fan_on)
        VALUES (?, ?, ?, ?, ?);
        """
        # 使用 ? 占位符可以防止SQL注入
        await self.conn.execute(
            sql, (datetime.now(), temperature, humidity, smoke_level, fan_on)
        )
        await self.conn.commit()
        # print("数据已写入数据库。") # 可以注释掉，避免日志过多

    async def get_latest_readings(self, limit: int = 100) -> List[Dict[str, Any]]:
        """获取最近的N条读数"""
        if not self.conn:
            raise RuntimeError("数据库未连接！")

        # aiosqlite.Connection 的 row_factory 默认是 tuple，我们设置为 aiosqlite.Row
        # 这样就可以像字典一样访问列
        self.conn.row_factory = aiosqlite.Row

        cursor = await self.conn.execute(
            "SELECT * FROM sensor_readings ORDER BY timestamp DESC LIMIT ?", (limit,)
        )
        rows = await cursor.fetchall()

        # 将 aiosqlite.Row 对象转换为普通字典，方便JSON序列化
        return [dict(row) for row in rows]
