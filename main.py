import pymysql


class EnvironmentDatabaseManager:
    def __init__(self, host, user, password):
        self.host = host
        self.user = user
        self.password = password
        self.database_name = "rpi_env_monitor"
        self.table_name = "environment_data"
        self._create_database()
        self._create_table()

    def _connect(self):
        return pymysql.connect(host=self.host, user=self.user, password=self.password)

    def _create_database(self):
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database_name}")

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

    def insert_env_data(self, temp, humid):
        with self._connect_to_db() as connection:
            with connection.cursor() as cursor:
                cursor.execute(f"""
                    INSERT INTO {self.table_name} (temperature, humidity) VALUES ({temp}, {humid})
                """)


if __name__ == "__main__":
    pass
