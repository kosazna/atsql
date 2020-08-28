# -*- coding: utf-8 -*-
from .computation import *


def transform_split(data: (str, pd.DataFrame)):
    if isinstance(data, str):
        df = pd.read_excel(data)
    else:
        df = data.copy()

    df['obj'] = df.apply(lambda p: Point(p['station'],
                                         p['X'],
                                         p['Y'],
                                         p['Z']), axis=1)

    df.set_index('station', drop=True, inplace=True)
    s = df['obj'].copy(deep=True)

    return df, s


class Container:
    def __init__(self, data: (str, pd.DataFrame)):
        self.data, self.series = transform_split(data)

    def __len__(self):
        return self.data.shape[0]

    def __getitem__(self, key):
        try:
            return self.series[key]
        except KeyError:
            print(f"[ERROR] - Point doesn't exist: [{key}]")
            return Point('ExceptionPoint', np.nan, np.nan, np.nan)

    def __setitem__(self, key, value):
        self.series[key] = value

    def update(self, other_data: pd.DataFrame):
        _original = self.data.copy(deep=True).reset_index()
        _new = other_data.copy().reset_index()

        _final = _original.append(_new).drop_duplicates(subset='station')

        self.data, self.series = transform_split(_final)

    def display(self):
        keep = ['X', 'Y', 'Z']
        return self.data[keep].copy()
