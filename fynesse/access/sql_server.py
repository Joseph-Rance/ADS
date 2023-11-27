import pymysql

from ..config import config

class SQLConnection:  # connection object stores credentials so
                      # we can reconnect if we get disconnected

    def __init__(self, credentials=None, database="property_prices"):

        if not credentials:
            credentials = self.get_credentials()

        self.credentials = credentials
        self.database = database
        self.connection = None

    def __repr__(self):
        return ("<open" if self.connection else "<closed") + \
               f" PyMySQL connection to {self.credentials['host']}>"

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
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{self.database}` \
                             DEFAULT CHARACTER SET utf8 COLLATE utf8_bin;")
        self.connection.commit()
        self.connection.select_db(self.database)

    def close(self):
        self.connection.close()

    def get(self):  # this provides an alive self.connection
        if not self.connection:
            self.open()
        self.connection.ping()
        self.connection.select_db(self.database)
        return self.connection

    instance = None

    @classmethod
    def get_instance(cls):  # this allows us to have a single global connection
        if cls.instance is None:
            cls.instance = cls()
        return cls.instance

def connect(f):  # decorator passes the global connection to the inner function
    def inner(*args, **kwargs):
        connection = SQLConnection.get_instance()
        return f(connection.get(), *args, **kwargs)
    return inner

@connect
def query_table(connection, query):
    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
    return rows

@connect
def update_table(connection, query):
    with connection.cursor() as cursor:
        cursor.execute(query)
    connection.commit()