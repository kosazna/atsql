# -*- coding: utf-8 -*-
from .traverse import *
from .taximetria import *
from datetime import datetime


def _load(data):
    if isinstance(data, str):
        return pd.read_excel(data)
    return data


def station2series(data: (str, pd.DataFrame)):
    if isinstance(data, str):
        df = pd.read_excel(data)
    else:
        df = data

    df['obj'] = df.apply(lambda p: Point(p['station'],
                                         p['X'],
                                         p['Y'],
                                         p['Z']), axis=1)

    df.set_index('station', drop=True, inplace=True)
    s = df['obj'].copy(deep=True)

    return s


def extract_workind_dir(data):
    if isinstance(data, str):
        return Path(data).parent
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
        self.t_data = _load(traverse_data)
        self.s_data = _load(sideshot_data)
        self.t_list = _load(traverses)
        self.stations = station2series(_load(stations))
        self.staseis = _load(stations).set_index('station', drop=True)
        self.working_dir = working_dir if working_dir else extract_workind_dir(
            traverses)

    def point2obj(self, points: list) -> List[Point]:
        return [self.stations[points[0]], self.stations[points[1]]]

    def station2obj(self, stations):
        df = stations.copy()
        df['obj'] = df.apply(lambda p: Point(p.index,
                                             p['X'],
                                             p['Y'],
                                             p['Z']), axis=1)

        return self.stations.append(df['obj']).drop_duplicates(inplace=True)

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

            self.staseis = self.staseis.append(tr.stations).drop_duplicates(
                inplace=True)
            self.stations = self.station2obj(tr.stations)

            print(tr)

            tr.export()

    def compute_taximetria(self):
        pass
