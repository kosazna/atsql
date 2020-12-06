from aztool_dw.core.dimension import *


class SQLStatements:
    def __init__(self, data: pd.DataFrame, dimensions: DimEncoder):
        self.data = data.copy(deep=True)
        self.dims = dimensions

    def dimension_create_statement(self, directory=None):
        if directory is None:
            file = 'dimension_tables.sql'
        else:
            file = f'{directory}\\dimension_tables.sql'

        with open(file, 'w') as sql_script:
            for dim in self.dims.dimensions.keys():
                sql_script.write(f"""CREATE TABLE d_{dim} (
                    {dim}_id INT NOT NULL,
                    {dim}_label VARCHAR(55),
                    PRIMARY KEY ({dim}_id));\n""")

    def fact_create_statement(self, table_name, directory=None):
        if directory is None:
            file = 'fact_table.sql'
        else:
            file = f'{directory}\\fact_table.sql'

        with open(file, 'w') as sql_script:
            sql_script.write(f"CREATE TABLE {table_name} (\n")
            for col in self.data.columns:
                col_type = self.data[col].dtype
                if str(col_type).lower().startswith('int'):
                    sql_script.write(f'\t`{col}` INT NOT NULL,\n')
                elif col_type == 'datetime64[ns]':
                    sql_script.write(f'\t`{col}` DATE NOT NULL,\n')
                else:
                    sql_script.write(f'\t`{col}` FLOAT NOT NULL,\n')

            for dim in self.dims.dimensions.keys():
                sql_script.write(f"""\tFOREIGN KEY (`{dim}`)
                REFERENCES d_{dim} ({dim}_id),\n""")
            sql_script.write(");")

    def dimension_insert_statement(self, directory=None):
        if directory is None:
            file = 'dimension_data.sql'
        else:
            file = f'{directory}\\dimension_data.sql'

        with open(file, 'w') as sql_script:
            for dim, data in self.dims.dimensions.items():
                for idx, label in data.items():
                    sql_script.write(
                        f"INSERT INTO d_{dim} (`{dim}_id`,`{dim}_label`)"
                        f" VALUES ({idx},'{label}');\n")

    def fact_insert_statements(self,
                               table_name,
                               directory=None,
                               na_values=None,
                               batch_size=2000):
        if directory is None:
            file = 'fact_data.sql'
        else:
            file = f'{directory}\\fact_data.sql'

        number_of_records = self.data.shape[0]
        all_inserts = []
        iterations = int(number_of_records / batch_size) + 1

        for i in range(iterations):
            start_idx = i * batch_size
            end = (i + 1) * batch_size
            end_idx = end if end < number_of_records else number_of_records

            insert_str = f'INSERT INTO {table_name} (' + ",".join(
                [f"`{col}`" for col in self.data.columns]) + ')' + ' VALUES '
            values = self.data.iloc[start_idx:end_idx].values.tolist()
            values_str = ",".join(list(map(str, map(tuple, values)))).replace(
                ' ', '') + ';'
            all_str = insert_str + values_str
            all_inserts.append(all_str)

        insert = '\n'.join(all_inserts)

        if na_values is not None:
            if isinstance(na_values, str):
                insert = insert.replace(na_values, 'NULL')
            else:
                for na_value in na_values:
                    insert = insert.replace(na_value, 'NULL')

        with open(file, 'w') as sql_script:
            sql_script.write(insert)
