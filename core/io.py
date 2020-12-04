# -*- coding: utf-8 -*-
import sqlalchemy as db
import os
import mysql.connector

mysql_password = os.environ.get('mysql_password')

config = {
    'user': 'root',
    'password': mysql_password,
    'host': '127.0.0.1',
}


def create_schema(schema_name):
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    query = f'CREATE SCHEMA `{schema_name}` DEFAULT CHARACTER SET utf8mb4;'
    cursor.execute(query)
    cursor.close()
    connection.close()


def mysql_connection(schema):
    engine = db.create_engine(
        f"mysql+mysqlconnector://root:{mysql_password}@localhost:3306/{schema}")

    return engine


def mysql_execute(schema, query):
    engine = mysql_connection(schema)
    with engine.connect() as connection:
        result = connection.execute(query)

    if result:
        for row in result:
            print(row)
