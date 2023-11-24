import pymysql

from ..config import config

def get_credentials():  # keys correspond to pymysql.connect named parameters
    return {"user": config["database_username"],
            "password": config["database_password"],
            "host": config["database_url"]
            "port": config["database_port"]}

def open_connection(credentials=None, database=None):
    if not credentials:
        credentials = get_credentials()
    connection = pymysql.connect(**credentials, database=database, local_infile=1)
    with connection.cursor() as cursor:
        cursor.execute("SET SQL_MODE = 'NO_AUTO_VALUE_ON_ZERO';")
        cursor.execute("SET time_zone = '+00:00';")
    connection.commit()
    return connection

def close_connection(connection):
    connection.close()

def use_database(connection, name):
    with connection.cursor() as cursor:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{name}`" \
                        "DEFAULT CHARACTER SET utf8 COLLATE utf8_bin;")
        cursor.execute("USE `property_prices`;")
    connection.commit()

def query_table(connection, query):
    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
    return rows