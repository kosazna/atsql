# -*- coding: utf-8 -*-
from .traverse import *
from .taximetria import *
from datetime import datetime


def load_stations(file: str):
    df = pd.read_excel(file)
    df['obj'] = df.apply(lambda p: Point(p['station'],
                                         p['X'],
                                         p['Y'],
                                         p['Z']), axis=1)

    df.set_index('station', drop=True, inplace=True)
    s = df['obj'].copy(deep=True)

    return s


class SurveyProject:
    def __init__(self,
                 name: str = None,
                 traverse_data: pd.DataFrame = None,
                 sideshot_data: pd.DataFrame = None,
                 traverses: pd.DataFrame = None,
                 stations: pd.Series = None):
        self.name = name
        self.time = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        self.traverse_data = traverse_data.copy()
        self.sideshot_data = sideshot_data.copy()
        self.traverses = traverses.copy()
        self.stations = stations.copy()
        self.data = pd.DataFrame()

    def point2obj(self, points: list) -> List[Point]:
        return [self.stations[points[0]], self.stations[points[1]]]

    def prepare_data(self):
        self.traverses['stations'] = self.traverses['stations'].str.split('-')
        self.traverses['start'] = self.traverses['stations'].apply(
            lambda x: x[:2])
        self.traverses['last'] = self.traverses['stations'].apply(
            lambda x: x[-2:])

    def compute_traverses(self):
        for traverse in self.traverses.itertuples():
            if traverse.t_type == 'LinkTraverse':
                tr = LinkTraverse(stops=traverse.stations,
                                  data=self.traverse_data,
                                  start=self.point2obj(traverse.start),
                                  finish=self.point2obj(traverse.last))
            elif traverse.t_type == 'ClosedTraverse':
                tr = ClosedTraverse(stops=traverse.stations,
                                    data=self.traverse_data,
                                    start=self.point2obj(traverse.start))
            else:
                tr = OpenTraverse(stops=traverse.stations,
                                  data=self.traverse_data,
                                  start=self.point2obj(traverse.start))

            tr.compute()
            self.data.append(tr.odeusi)
            # tr.export()
            print(tr)

    def compute_taximetria(self):
        pass
