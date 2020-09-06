# -*- coding: utf-8 -*-
from .misc import *
from pathlib import Path
from shutil import copy


def copy_shp(file: (str, Path), dst: (str, Path)):
    _file = Path(file)
    copy(_file, dst)
    copy(_file.with_suffix('.dbf'), dst)
    copy(_file.with_suffix('.shx'), dst)


def export_shp(data: pd.DataFrame, dst: (str, Path), name: str, round_z=2):
    import geopandas as gpd
    _data = data.copy().reset_index().rename(columns={'station': 'ID'}).round(4)
    _data['ID'] = _data['ID'].astype(str)
    _data['display_Z'] = _data['Z'].round(round_z).astype(str)
    _geometry = gpd.points_from_xy(_data['X'], _data['Y'], _data['Z'])
    gdf = gpd.GeoDataFrame(_data, geometry=_geometry)

    output = Path(dst).joinpath(f'{name}.shp')

    gdf.to_file(output)
