# -*- coding: utf-8 -*-
from .computation import *


def station2series(data: (str, pd.DataFrame)):
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
        self.data, self.series = station2series(data)

    def __len__(self):
        return self.data.shape[0]

    def __getitem__(self, key):
        return self.series[key]

    def __setitem__(self, key, value):
        self.series[key] = value

    def __repr__(self):
        pass

    # def __add__(self, other: pd.DataFrame):
    #     self.data = self.data.reset_index().append(
    #         other.reset_index(drop=True)).drop_duplicates(
    #         subset='station').set_index('station', drop=True)
    #
    #     self.series = self.data['obj']

    def update(self, other_data: pd.DataFrame):
        _original = self.data.copy(deep=True).reset_index()
        _new = other_data.copy().reset_index()

        _final = _original.append(_new).drop_duplicates(subset='station')

        self.data, self.series = station2series(_final)

    def display(self):
        keep = ['X', 'Y', 'Z']
        return self.data[keep].copy()
