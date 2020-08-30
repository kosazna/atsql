# -*- coding: utf-8 -*-
from .computation import *


def transform_split(data: (str, pd.DataFrame)):
    if isinstance(data, str):
        df = pd.read_excel(data)
    else:
        df = data.copy()

    if df.index.name == 'station':
        df.reset_index(inplace=True)

    df['obj'] = df.apply(lambda p: Point(p['station'],
                                         p['X'],
                                         p['Y'],
                                         p['Z']), axis=1)

    df.set_index('station', drop=True, inplace=True)
    s = df['obj'].copy(deep=True)

    return df, s


class Container:
    def __init__(self, data: (str, pd.DataFrame)):
        self._data, self._series = transform_split(data)

    def __len__(self):
        return self._data.shape[0]

    def __getitem__(self, key):
        try:
            return self._series[key]
        except KeyError:
            print(f"[ERROR] - Point doesn't exist: [{key}]")
            return Point('ExceptionPoint', np.nan, np.nan, np.nan)

    def __setitem__(self, key, value):
        self._series[key] = value

    def __call__(self):
        keep = ['X', 'Y', 'Z']
        return self._data[keep].copy()

    def __contains__(self, item):
        if isinstance(item, str):
            return item in self._data.index
        elif isinstance(item, (list, tuple)):
            return all([i in self._data.index for i in item])

    def update(self, other_data: pd.DataFrame):
        _original = self._data.copy(deep=True).reset_index()
        _new = other_data.copy().reset_index()

        _final = _original.append(_new).drop_duplicates(subset='station')

        self._data, self._series = transform_split(_final)

