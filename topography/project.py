# -*- coding: utf-8 -*-
from .traverse import *
from .taximetria import *
from .data import *
from datetime import datetime


def _load(data, sheet_name: str = None):
    if isinstance(data, str):
        _sheet = 0 if sheet_name is None else sheet_name
        return pd.read_excel(data, sheet_name=_sheet)
    return data


def extract_workind_dir(data):
    if isinstance(data, str):
        _path = Path(data)
        return _path if _path.is_dir() else _path.parent
    elif isinstance(data, Path):
        return data if data.is_dir() else data.parent
    else:
        raise IsADirectoryError("""Working directory can't be infered from data.
        Provide 'working_dir' when instantiating the class SurveyProject.""")


class SurveyProject:
    def __init__(self,
                 name: str = None,
                 traverse_data: (str, pd.DataFrame) = None,
                 sideshot_data: (str, pd.DataFrame) = None,
                 traverses: (str, pd.DataFrame) = None,
                 stations: (str, pd.DataFrame) = None,
                 working_dir: (str, Path) = None):
        self.name = name
        self.time = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        self.t_data = _load(traverse_data, sheet_name='Traverse_Measurements')
        self.s_data = _load(sideshot_data, sheet_name='Taximetrika')
        self.t_list = _load(traverses)
        self.stations = Container(stations)
        self.sideshots = Container(stations)
        self.working_dir = working_dir if working_dir else extract_workind_dir(
            traverses)

    def point2obj(self, points: (list, tuple)) -> List[Point]:
        return [self.stations[points[0]], self.stations[points[1]]]

    def prepare_data(self):
        self.t_list['stations'] = self.t_list['stations'].str.split('-')
        self.t_list['start'] = self.t_list['stations'].apply(
            lambda x: x[:2])
        self.t_list['last'] = self.t_list['stations'].apply(
            lambda x: x[-2:])

    def compute_traverses(self):
        for traverse in self.t_list.itertuples():
            if traverse.t_type == 'LinkTraverse':
                tr = LinkTraverse(stops=traverse.stations,
                                  data=self.t_data,
                                  start=self.point2obj(traverse.start),
                                  finish=self.point2obj(traverse.last),
                                  working_dir=self.working_dir)
            elif traverse.t_type == 'ClosedTraverse':
                tr = ClosedTraverse(stops=traverse.stations,
                                    data=self.t_data,
                                    start=self.point2obj(traverse.start),
                                    working_dir=self.working_dir)
            else:
                tr = OpenTraverse(stops=traverse.stations,
                                  data=self.t_data,
                                  start=self.point2obj(traverse.start),
                                  working_dir=self.working_dir)

            tr.compute()

            self.stations.update(tr.stations)
            print(tr)
            tr.export()

    def compute_taximetria(self):
        self.sideshots.update(self.stations.display())

        point_groups = self.s_data.groupby(['station', 'bs'])

        for group in point_groups.groups:
            if group[0] in self.stations.data.index and \
                    group[1] in self.stations.data.index:
                _data = point_groups.get_group(group)
                ss = Sideshot(_data,
                              self.stations[group[0]],
                              self.stations[group[1]])

                ss.compute()
                self.sideshots.update(ss.points)
