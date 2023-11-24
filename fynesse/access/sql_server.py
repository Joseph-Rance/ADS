import pymysql

from ..config import config

class SQLConnection:  # connection object stores credentials so
                      # we can reconnect if we get disconnected

    def __init__(self, credentials=None):

        if not credentials:
            credentials = self.get_credentials()

        self.credentials = credentials
        self.connection = None

    def get_credentials(self):  # keys correspond to pymysql.connect named parameters
        return {"user": config["database_username"],
                "password": config["database_password"],
                "host": config["database_url"],
                "port": config["database_port"]}

    def open(self):
        self.connection = pymysql.connect(**self.credentials, local_infile=1)
        with self.connection.cursor() as cursor:
            cursor.execute("SET SQL_MODE = 'NO_AUTO_VALUE_ON_ZERO';")
            cursor.execute("SET time_zone = '+00:00';")
        self.connection.commit()

    def close(self):
        self.connection.close()

    def get(self):
        if not self.connection:
            self.open()
        self.connection.ping()
        return self.connection

    instance = None

    @classmethod
    def get_instance(cls):  # this allows us to have a single global connection
        if cls.instance is None:
            cls.instance = cls()
        return cls.instance

def connect(f):  # decorator passes in the global connection
    def inner(*args, **kwargs):
        connection = SQLConnection.get_instance()
        f(connection.get(), *args, **kwargs)
    return inner

@connect
def use_database(connection, name):
    with connection.cursor() as cursor:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{name}`" \
                        "DEFAULT CHARACTER SET utf8 COLLATE utf8_bin;")
        cursor.execute("USE `property_prices`;")
    connection.commit()

@connect
def query_table(connection, query):
    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
    return rows