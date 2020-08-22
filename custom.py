# -*- coding: utf-8 -*-
import pandas as pd
import sqlalchemy as db
import matplotlib.pyplot as plt
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


def plt_info(title, xlabel, ylabel, color='k', save_name=''):
    plt.title(title, fontsize=18)
    plt.xlabel(xlabel, fontsize=14, color=color)
    plt.ylabel(ylabel, fontsize=14, color=color)

    plt.savefig(save_name, bbox_inches='tight')


def column_statistics(data: pd.DataFrame):
    data_dict = {col: {'unique': data[col].value_counts().index.to_list(),
                       'unique_count': len(data[col].unique()),
                       'value_counts': data[col].value_counts()}
                 for col in data.columns if data[col].dtype != 'datetime64[ns]'}

    stats_df = pd.DataFrame.from_dict(data_dict, orient='index',
                                      columns=['unique', 'unique_count',
                                               'value_counts'])

    return stats_df


def dict_to_csv(d, name, columns, directory=None, orient='index'):
    d_frame = pd.DataFrame.from_dict(d, orient=orient, columns=columns[1:])
    d_frame.reset_index(inplace=True)
    d_frame.columns = columns
    d_frame.to_csv(f'{directory}\\' + f'{name}.csv', index=False)


class DimEncoder:
    def __init__(self, data: pd.DataFrame, columns: list):
        self.data = data.copy(deep=True)
        self.columns = columns
        self.reversed_dimensions = dict.fromkeys(columns)
        self.dimensions = dict.fromkeys(columns)

    def fit(self, start=1):
        for column in self.columns:
            mapper = dict(enumerate(sorted(self.data[column].unique()), start))
            reversed_mapper = dict(zip(mapper.values(), mapper.keys()))

            self.dimensions[column] = mapper
            self.reversed_dimensions[column] = reversed_mapper

        print(f'Created {len(self.reversed_dimensions.keys())} dimensions.')

    def export_to_csv(self, directory=None):
        for column in self.columns:
            dict_to_csv(self.dimensions[column], name=f'{column}_dim',
                        columns=[f'{column}_id', f'{column}_label'],
                        directory=directory)

            print(f'Exported "{column}" dimension as : {column}_dim.csv.')

    def transform(self) -> pd.DataFrame:
        for dimension, mapper in self.reversed_dimensions.items():
            self.data[dimension] = self.data[dimension].map(mapper)

        return self.data

    def reverse_tranform(self, data) -> pd.DataFrame:
        for dimension, mapper in self.dimensions.items():
            data[dimension] = data[dimension].map(mapper)

        return data


class SQLStatements:
    def __init__(self, data: pd.DataFrame, dimensions: DimEncoder):
        self.data = data.copy(deep=True)
        self.dims = dimensions

    def dimension_statement(self, directory=None):
        if directory is None:
            file = 'dimension_tables.sql'
        else:
            file = f'{directory}\\dimension_tables.sql'

        with open(file, 'w') as sql_script:
            for dim in self.dims.dimensions.keys():
                sql_script.write(f"""CREATE TABLE d_{dim} (
                    {dim}_id INT NOT NULL,
                    {dim}_label VARCHAR(50),
                    PRIMARY KEY ({dim}_id));\n""")

    def fact_statement(self, table_name, directory=None):
        if directory is None:
            file = 'fact_table.sql'
        else:
            file = f'{directory}\\fact_table.sql'

        with open(file, 'w') as sql_script:
            sql_script.write(f"CREATE TABLE {table_name} (\n")
            for col in self.data.columns:
                col_type = self.data[col].dtype
                if col_type == 'int64':
                    sql_script.write(f'\t`{col}` INT NOT NULL,\n')
                elif col_type == 'datetime64[ns]':
                    sql_script.write(f'\t`{col}` DATE NOT NULL,\n')
                else:
                    sql_script.write(f'\t`{col}` FLOAT NOT NULL,\n')

            for dim in self.dims.dimensions.keys():
                sql_script.write(f"""\tFOREIGN KEY (`{dim}`)
                REFERENCES d_{dim} ({dim}_id),\n""")
            sql_script.write(");")

    def dimension_data_statement(self, directory=None):
        if directory is None:
            file = 'dimension_data.sql'
        else:
            file = f'{directory}\\dimension_data.sql'

        with open(file, 'w') as sql_script:
            for dim, data in self.dims.dimensions.items():
                for id, label in data.items():
                    sql_script.write(
                        f"INSERT INTO d_{dim} (`{dim}_id`,`{dim}_label`) VALUES ({id},'{label}');\n")
