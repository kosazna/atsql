from typing import List
from topography.computation import *


def join_stops_for_angle(stops):
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


def join_stops_for_dist(stops):
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


class Traverse:
    def __init__(self, stops: list,
                 data: pd.DataFrame = None,
                 start: List[Point] = None):
        self.stops = stops
        self.stops_count = len(stops)
        self.length = 0
        self.metriseis = data
        self.first1 = start[0] if start else None
        self.first2 = start[1] if start else None
        self.a_start = self.first1.azimuth(self.first2)
        self.odeusi = pd.merge(pd.DataFrame(
            list(zip(join_stops_for_angle(stops), join_stops_for_dist(stops))),
            columns=['angle', 'distance']), self.metriseis, on='angle',
            how='left')

    @property
    def mean_elevation(self):
        return round((self.first2.z + self.first1.z) / 2, 3)

    @property
    def k(self):
        return round8(calc_k(self.first2.x, self.first1.x))

    @classmethod
    def from_excel(cls, file: str, stops: list, known: List[Point] = None):
        data = pd.read_excel(file)
        return cls(stops, data, known)

    def __repr__(self):
        msg = f"""
            Traverse stops: {'-'.join(self.stops)}  [{self.stops_count}]\n
            Traverse length: {self.length:.3f}
            Mean Elevation: {self.mean_elevation}
            k: {self.k:.4f}\n
            α{self.first1.name}-{self.first2.name} : {self.a_start:.4f}"""

        return msg

    def compute(self):
        self.odeusi.loc[self.odeusi.index[-1], ['h_dist', 'dz_temp']] = np.nan
        self.odeusi.loc[self.odeusi.index[-1], 'distance'] = np.nan

        self.odeusi['surf_dist'] = surface_distance(self.odeusi['h_dist'],
                                                    self.mean_elevation)
        self.odeusi['egsa_dist'] = egsa_distance(self.odeusi['surf_dist'],
                                                 self.k)

        self.length = self.odeusi['egsa_dist'].sum()

        self.odeusi['azimuth'] = 0

        hold = self.a_start

        for i in self.odeusi.itertuples():
            _a = hold + i.h_angle + 200
            if _a > 400:
                a = _a % 400
            else:
                a = _a
            hold = a
            self.odeusi.loc[i.Index, 'azimuth'] = a

        self.odeusi['dx_temp'] = self.odeusi['egsa_dist'] * np.sin(
            grad_to_rad(self.odeusi['azimuth']))

        self.odeusi['dy_temp'] = self.odeusi['egsa_dist'] * np.cos(
            grad_to_rad(self.odeusi['azimuth']))

        self.odeusi['dX'] = self.odeusi['dx_temp']
        self.odeusi['dY'] = self.odeusi['dy_temp']
        self.odeusi['dZ'] = self.odeusi['dz_temp']

        self.odeusi[['bs', 'STATION', 'fs']] = self.odeusi['angle'].str.split(
            '-', expand=True)

        keep = ['bs', 'STATION', 'fs',
                'h_dist', 'surf_dist', 'egsa_dist',
                'h_angle', 'azimuth',
                'dX', 'dY', 'dZ']

        self.odeusi = self.odeusi[keep]

        self.odeusi['X'] = 0
        self.odeusi['Y'] = 0
        self.odeusi['Z'] = 0

        self.odeusi.loc[
            self.odeusi['STATION'] == self.first2.name, 'X'] = self.first2.x
        self.odeusi.loc[
            self.odeusi['STATION'] == self.first2.name, 'Y'] = self.first2.y
        self.odeusi.loc[
            self.odeusi['STATION'] == self.first2.name, 'Z'] = self.first2.z

        hold_x = self.odeusi.loc[
            self.odeusi['STATION'] == self.first2.name, 'X'][0]
        hold_y = self.odeusi.loc[
            self.odeusi['STATION'] == self.first2.name, 'Y'][0]
        hold_z = self.odeusi.loc[
            self.odeusi['STATION'] == self.first2.name, 'Z'][0]
        hold_dx = self.odeusi.loc[
            self.odeusi['STATION'] == self.first2.name, 'dX'][0]
        hold_dy = self.odeusi.loc[
            self.odeusi['STATION'] == self.first2.name, 'dY'][0]
        hold_dz = self.odeusi.loc[
            self.odeusi['STATION'] == self.first2.name, 'dZ'][0]

        for i in self.odeusi.itertuples():
            if i.STATION == self.first2.name:
                pass
            else:
                self.odeusi.loc[i.Index, 'X'] = hold_x + hold_dx
                self.odeusi.loc[i.Index, 'Y'] = hold_y + hold_dy
                self.odeusi.loc[i.Index, 'Z'] = hold_z + hold_dz
                hold_x = hold_x + hold_dx
                hold_y = hold_y + hold_dy
                hold_z = hold_z + hold_dz
                hold_dx, hold_dy, hold_dz = i.dX, i.dY, i.dZ

    def export(self):
        file_to_export = self.odeusi.copy()
        prefix = f'PT_{self.first1.name}-{self.first2.name}'
        suffix = '_one_anchor'
        name = '-'.join([prefix, suffix])
        file_to_export.round8(4).to_excel(f'{name}.xlsx', index=False)

        file_to_export = file_to_export[['STATION', 'X', 'Y', ]]

        file_to_export.round8(4).to_excel(f'Staseis_{name}.xlsx', index=False)


class ClosedTraverse(Traverse):
    def __init__(self, stops: list,
                 data: pd.DataFrame = None,
                 start: List[Point] = None,
                 finish: List[Point] = None):

        super().__init__(stops=stops, data=data, start=start)
        self.last1 = finish[-2] if finish else None
        self.last2 = finish[-1] if finish else None
        self.a_finish = self.last1.azimuth(self.last2)
        self._last1_temp_x = 0
        self._last1_temp_y = 0
        self._last1_temp_z = 0

    @property
    def mean_elevation(self):
        return round((self.first2.z + self.last1.z) / 2, 3)

    @property
    def k(self):
        return round8(calc_k(self.first2.x, self.last1.x))

    @property
    def a_measured(self):
        return azimuth_from_measurements(self.a_start, self.odeusi['h_angle'])

    @property
    def angular_correction(self):
        return round8(self.angular_misclosure / self.odeusi.shape[0])

    @property
    def angular_misclosure(self):
        return round8(self.a_finish - self.a_measured)

    @property
    def horizontal_misclosure(self):
        return round8(np.sqrt(self.wx ** 2 + self.wy ** 2))

    @property
    def wx(self):
        return round8(self.last1.x - self._last1_temp_x)

    @property
    def wy(self):
        return round8(self.last1.y - self._last1_temp_y)

    @property
    def wz(self):
        return round8(self.last1.z - self._last1_temp_z)

    @property
    def x_cor(self):
        try:
            return self.wx / self.length
        except ZeroDivisionError:
            return 0

    @property
    def y_cor(self):
        try:
            return self.wy / self.length
        except ZeroDivisionError:
            return 0

    @property
    def z_cor(self):
        try:
            return self.wz / self.length
        except ZeroDivisionError:
            return 0

    @classmethod
    def from_excel(cls, file: str, stops: list, known: List[Point] = None):
        data = pd.read_excel(file)
        return cls(stops, data, known)

    def __repr__(self):
        msg = f"""
            Traverse stops: {'-'.join(self.stops)}  [{self.stops_count}]\n
            Traverse length: {self.length:.3f}
            Mean Elevation: {self.mean_elevation}
            k: {self.k:.4f}\n
            α{self.first1.name}-{self.first2.name} : {self.a_start:.4f}
            α{self.last1.name}-{self.last2.name} : {self.a_finish:.4f}
            α'{self.last1.name}-{self.last2.name} : {self.a_measured:.4f}
            Angular Misclosure: {self.angular_misclosure:+.4f}
            Angular Correction: {self.angular_correction:+.4f}\n
            Horizontal Misclosure: {self.horizontal_misclosure:.3f}
            wX: {self.wx:+.3f}
            wY: {self.wy:+.3f}
            wZ: {self.wz:+.3f}"""

        return msg

    def compute(self):
        self.odeusi.loc[self.odeusi.index[-1], ['h_dist', 'dz_temp']] = np.nan
        self.odeusi.loc[self.odeusi.index[-1], 'distance'] = np.nan

        self.odeusi['surf_dist'] = surface_distance(self.odeusi['h_dist'],
                                                    self.mean_elevation)
        self.odeusi['egsa_dist'] = egsa_distance(self.odeusi['surf_dist'],
                                                 self.k)

        self.length = self.odeusi['egsa_dist'].sum()

        self.odeusi['h_angle_fixed'] = self.odeusi[
                                           'h_angle'] + self.angular_correction

        self.odeusi['azimuth'] = 0

        hold = self.a_start

        for i in self.odeusi.itertuples():
            _a = hold + i.h_angle_fixed + 200
            if _a > 400:
                a = _a % 400
            else:
                a = _a
            hold = a
            self.odeusi.loc[i.Index, 'azimuth'] = a

        self.odeusi['dx_temp'] = self.odeusi['egsa_dist'] * np.sin(
            grad_to_rad(self.odeusi['azimuth']))

        self.odeusi['dy_temp'] = self.odeusi['egsa_dist'] * np.cos(
            grad_to_rad(self.odeusi['azimuth']))

        self._last1_temp_x = self.first2.x + self.odeusi['dx_temp'].sum()
        self._last1_temp_y = self.first2.y + self.odeusi['dy_temp'].sum()
        self._last1_temp_z = self.first2.z + self.odeusi['dz_temp'].sum()

        self.odeusi['dX'] = self.odeusi['dx_temp'] + self.x_cor * self.odeusi[
            'egsa_dist']
        self.odeusi['dY'] = self.odeusi['dy_temp'] + self.y_cor * self.odeusi[
            'egsa_dist']
        self.odeusi['dZ'] = self.odeusi['dz_temp'] + self.z_cor * self.odeusi[
            'egsa_dist']

        self.odeusi[['bs', 'STATION', 'fs']] = self.odeusi['angle'].str.split(
            '-', expand=True)

        keep = ['bs', 'STATION', 'fs',
                'h_dist', 'surf_dist', 'egsa_dist',
                'h_angle', 'h_angle_fixed', 'azimuth',
                'dX', 'dY', 'dZ']

        self.odeusi = self.odeusi[keep]

        self.odeusi['X'] = 0
        self.odeusi['Y'] = 0
        self.odeusi['Z'] = 0

        self.odeusi.loc[
            self.odeusi['STATION'] == self.first2.name, 'X'] = self.first2.x
        self.odeusi.loc[
            self.odeusi['STATION'] == self.first2.name, 'Y'] = self.first2.y
        self.odeusi.loc[
            self.odeusi['STATION'] == self.first2.name, 'Z'] = self.first2.z

        hold_x = self.odeusi.loc[
            self.odeusi['STATION'] == self.first2.name, 'X'][0]
        hold_y = self.odeusi.loc[
            self.odeusi['STATION'] == self.first2.name, 'Y'][0]
        hold_z = self.odeusi.loc[
            self.odeusi['STATION'] == self.first2.name, 'Z'][0]
        hold_dx = self.odeusi.loc[
            self.odeusi['STATION'] == self.first2.name, 'dX'][0]
        hold_dy = self.odeusi.loc[
            self.odeusi['STATION'] == self.first2.name, 'dY'][0]
        hold_dz = self.odeusi.loc[
            self.odeusi['STATION'] == self.first2.name, 'dZ'][0]

        for i in self.odeusi.itertuples():
            if i.STATION == self.first2.name:
                pass
            elif i.STATION == self.last1.name:
                self.odeusi.loc[i.Index, 'X'] = self.last1.x
                self.odeusi.loc[i.Index, 'Y'] = self.last1.y
                self.odeusi.loc[i.Index, 'Z'] = self.last1.z
            else:
                self.odeusi.loc[i.Index, 'X'] = hold_x + hold_dx
                self.odeusi.loc[i.Index, 'Y'] = hold_y + hold_dy
                self.odeusi.loc[i.Index, 'Z'] = hold_z + hold_dz
                hold_x = hold_x + hold_dx
                hold_y = hold_y + hold_dy
                hold_z = hold_z + hold_dz
                hold_dx, hold_dy, hold_dz = i.dX, i.dY, i.dZ

    def export(self):
        file_to_export = self.odeusi.copy()
        prefix = f'PT_{self.first1.name}-{self.first2.name}'
        suffix = f'{self.last1.name}-{self.last2.name}'
        name = '-'.join([prefix, suffix])
        file_to_export.round8(4).to_excel(f'{name}.xlsx', index=False)

        file_to_export = file_to_export[['STATION', 'X', 'Y', ]]

        file_to_export.round8(4).to_excel(f'Staseis_{name}.xlsx', index=False)
