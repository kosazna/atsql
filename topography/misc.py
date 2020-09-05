# -*- coding: utf-8 -*-
import shutil
import pandas as pd
import numpy as np
from pathlib import Path


def copy_shp(file: (str, Path), dst: (str, Path)):
    _file = Path(file)
    shutil.copy(_file, dst)
    shutil.copy(_file.with_suffix('.dbf'), dst)
    shutil.copy(_file.with_suffix('.shx'), dst)


def export_shp(data: pd.DataFrame, dst: (str, Path), name: str, round_z=2):
    import geopandas as gpd
    _data = data.copy().reset_index().rename(columns={'station': 'ID'}).round(4)
    _data['ID'] = _data['ID'].astype(str)
    _data['display_Z'] = _data['Z'].round(round_z).astype(str)
    _geometry = gpd.points_from_xy(_data['X'], _data['Y'], _data['Z'])
    gdf = gpd.GeoDataFrame(_data, geometry=_geometry)

    output = Path(dst).joinpath(f'{name}.shp')

    gdf.to_file(output)


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


def create_data(metriseis: str):
    df = pd.read_csv(metriseis, index_col='stop')
    return df


def infer_working_dir(file: (str, Path)):
    if isinstance(file, Path):
        _path = file
    else:
        _path = Path(file)

    if str(_path.parent).startswith('RAW') or \
            str(_path.parent).endswith('Processed') or \
            str(_path.parent).endswith('Transformed'):
        return _path.parent.parent
    else:
        return _path.parent
