# -*- coding: utf-8 -*-
from .traverse import *
from .taximetria import *
from datetime import datetime


def load_stations1(file: str):
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
                 stations: pd.DataFrame = None):
        self.name = name
        self.time = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        self.traverse_data = traverse_data
        self.sideshot_data = sideshot_data
        self.traverses = traverses
        self.stations = stations

    def prepare_data(self):
        self.traverses['stations'] = self.traverses['stations'].str.split('-')
        self.traverses['start'] = self.traverses['stations'].apply(
            lambda x: x[:2])
        self.traverses['last'] = self.traverses['stations'].apply(
            lambda x: x[-2:])

    def compute_traverses(self):
        SurveyProject.prepare_data(self)
        for traverse in self.traverses.itertuples():
            if traverse.t_type == 'LinkTraverse':
                tr = LinkTraverse(stops=traverse.stations,
                                  data=self.traverse_data,
                                  start=traverse.start,
                                  finish=traverse.last)
            elif traverse.t_type == 'ClosedTraverse':
                tr = ClosedTraverse(stops=traverse.stations,
                                    data=self.traverse_data,
                                    start=traverse.start)
            else:
                tr = OpenTraverse(stops=traverse.stations,
                                  data=self.traverse_data,
                                  start=traverse.start)

            tr.compute()
            tr.export()

    def compute_taximetria(self):
        pass
