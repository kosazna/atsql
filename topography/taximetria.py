# -*- coding: utf-8 -*-
from .data import *


class Sideshot:
    def __init__(self,
                 data: pd.DataFrame,
                 station: Point = None,
                 bs: Point = None):
        self.tm = data.copy()
        self.points = None
        self.station = station
        self.bs = bs
        self.a = station.azimuth(bs)
        self.mean_elevation = round((self.station.z + self.bs.z) / 2, 3)
        self.k = calc_k(station.x, bs.x)

    def compute(self):
        self.tm['h_dist'] = slope_to_hor(self.tm['slope_dist'],
                                         self.tm['v_angle'])

        self.tm['surf_dist'] = surface_distance(self.tm['h_dist'],
                                                self.mean_elevation)

        self.tm['egsa_dist'] = egsa_distance(self.tm['surf_dist'],
                                             self.k)

        self.tm['azimuth'] = azimuth_from_measurement(self.a,
                                                      self.tm['h_angle'])

        self.tm['X'] = calc_X(self.station.x,
                              self.tm['egsa_dist'],
                              self.tm['azimuth'])

        self.tm['Y'] = calc_Y(self.station.x,
                              self.tm['egsa_dist'],
                              self.tm['azimuth'])

        self.tm['Z'] = calc_Z(self.station.z,
                              self.tm['slope_dist'],
                              self.tm['v_angle'],
                              self.tm['station_h'],
                              self.tm['target_h'])

        self.tm['station'] = self.tm['fs']

        self.points = Container(self.tm[['station', 'X', 'Y', 'Z']])
