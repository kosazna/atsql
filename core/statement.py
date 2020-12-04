from aztool_dw.core.dimension import *


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
