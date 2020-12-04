# -*- coding: utf-8 -*-
from aztool_dw.util.misc import *


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
