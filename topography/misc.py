# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np


def round8(numbers):
    return round(numbers, 8)


def vectorize(func):
    def wrapper(*args, **kwargs):
        vector = False

        for i in args:
            if isinstance(i, (np.ndarray, pd.core.series.Series)):
                vector = True
                break

        if not vector:
            for i in kwargs:
                if isinstance(kwargs[i], (np.ndarray, pd.core.series.Series)):
                    vector = True
                    break

        if vector:
            vfunc = np.vectorize(func)
        else:
            vfunc = func

        result = vfunc(*args, **kwargs)

        return result

    return wrapper


def fmt_angle(stops):
    joined_stops = []
    for i, stop in enumerate(stops):
        if i == 0:
            pass
        else:
            try:
                joined_stops.append(f'{stops[i - 1]}-{stop}-{stops[i + 1]}')
            except IndexError:
                pass

    return joined_stops


def fmt_dist(stops):
    joined_stops = []
    for i, stop in enumerate(stops):
        if i == 0:
            pass
        else:
            try:
                joined_stops.append(f'{stop}-{stops[i + 1]}')
            except IndexError:
                pass

    return joined_stops


def join_stops_for_angle(midenismos, stasi, metrisi):
    return '-'.join([midenismos, stasi, metrisi])


def join_stops_for_dist(station, fs):
    return '-'.join(sorted([station, fs]))


def meas_type(fs: str, h_angle: float):
    if fs[0].isalpha() and h_angle == 0.0:
        return 'midenismos'
    elif fs[0].isalpha():
        return 'stasi'
    else:
        return 'taximetriko'
