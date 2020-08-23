# -*- coding: utf-8 -*-
from .misc import *

EARTH_C = 6371000


class Point:
    def __init__(self, name: str,
                 x: float = 0.0,
                 y: float = 0.0,
                 z: float = 0.0):

        self.name = name
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self) -> str:
        return f"{self.name:<6}({self.x:<10.3f},{self.y:<11.3f},{self.z:<7.3f})"

    @property
    def cords(self):
        return tuple([self.x, self.y, self.z])

    def split(self):
        return tuple([self.name, self.cords])

    def azimuth(self, point, reverse: bool = False) -> float:
        dx = point.x - self.x
        dy = point.y - self.y

        delta = round8(np.arctan(abs(dx) / abs(dy)))
        delta_grad = rad_to_grad(delta)

        if dx > 0 and dy > 0:
            return delta_grad if not reverse else 400 - delta_grad
        elif dx > 0 and dy < 0:
            return 200 - delta_grad if not reverse else 200 + delta_grad
        elif dx < 0 and dy < 0:
            return 200 + delta_grad if not reverse else 200 - delta_grad
        elif dx < 0 and dy > 0:
            return 400 - delta_grad if not reverse else delta_grad

    def distance(self, point) -> float:
        dx = point.x - self.x
        dy = point.y - self.y

        return round8(np.sqrt(dx ** 2 + dy ** 2))


@vectorize
def grad_to_rad(angle):
    return round8((angle * np.pi) / 200)


@vectorize
def rad_to_grad(angle):
    return round8((angle * 200) / np.pi)


@vectorize
def slope_to_hor(distance, angle):
    return round8(distance * np.sin(grad_to_rad(angle)))


@vectorize
def p2p_dh(distance, angle, uo, us):
    return round8(distance * np.cos(grad_to_rad(angle)) + uo - us)


def calc_k(x1, x2):
    x_sum = x1 + x2
    _ = (12311 * ((((x_sum / 2) * (10 ** -6)) - 0.5) ** 2) - 400) * (10 ** -6)
    return round8(1 + _)


@vectorize
def mean_dh_signed(original, mean):
    if original > 0:
        return mean
    else:
        return 0 - mean


def traverse_azimuth(measurements: pd.DataFrame, a_start: float):
    hold = a_start
    for i in measurements.itertuples():
        _a = hold + i.h_angle_fixed + 200
        if _a > 400:
            a = round(_a % 400, 6)
        else:
            a = round(_a, 6)
        hold = a

        measurements.loc[i.Index, 'azimuth'] = a


@vectorize
def surface_distance(dist, mean_elevation):
    return round8(dist * (EARTH_C / (EARTH_C + mean_elevation)))


@vectorize
def egsa_distance(dist, k=0.9996):
    return round8(dist * k)


@vectorize
def pt2tuple(point: Point):
    return tuple([point.x, point.y, point.z])


@vectorize
def azimuth_from_cords(a: (tuple, Point, np.ndarray, pd.core.series.Series),
                       b: (tuple, Point, np.ndarray, pd.core.series.Series),
                       reverse: bool = False,
                       point_object: bool = False):
    if point_object:
        dx = b.x - a.x
        dy = b.y - a.y
    else:
        dx = b[0] - a[0]
        dy = b[1] - a[1]

    delta = round8(np.arctan(abs(dx) / abs(dy)))
    delta_grad = rad_to_grad(delta)

    if dx > 0 and dy > 0:
        return delta_grad if not reverse else 400 - delta_grad
    elif dx > 0 and dy < 0:
        return 200 - delta_grad if not reverse else 200 + delta_grad
    elif dx < 0 and dy < 0:
        return 200 + delta_grad if not reverse else 200 - delta_grad
    elif dx < 0 and dy > 0:
        return 400 - delta_grad if not reverse else delta_grad


@vectorize
def distance_from_cords(a: (tuple, Point, np.ndarray, pd.core.series.Series),
                        b: (tuple, Point, np.ndarray, pd.core.series.Series),
                        point_object: bool = False):
    if point_object:
        dx = b.x - a.x
        dy = b.y - a.y
    else:
        dx = b[0] - a[0]
        dy = b[1] - a[1]

    return round8(np.sqrt(dx ** 2 + dy ** 2))


def azimuth_from_measurements(start,
                              measurements: (list,
                                             np.array,
                                             pd.core.series.Series)) -> float:
    am = start + round(sum(measurements), 6) + measurements.count() * 200

    return round(am % 400, 6)


@vectorize
def azimuth_from_measurement(start,
                             measurement):
    am = start + measurement + 200

    return round(am % 400, 6)


@vectorize
def calc_X(init_x, distance, azimuth):
    return round8(init_x + distance * np.sin(grad_to_rad(azimuth)))


@vectorize
def calc_Y(init_y, distance, azimuth):
    return round8(init_y + distance * np.cos(grad_to_rad(azimuth)))


@vectorize
def calc_Z(init_z, distance, angle, uo, us):
    return round8(init_z + p2p_dh(distance, angle, uo, us))
