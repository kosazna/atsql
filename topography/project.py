# -*- coding: utf-8 -*-
from .traverse import *
from .taximetria import *
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


def styler(data: pd.DataFrame, formatter: dict):
    return data.style.format(formatter).apply(warning,
                                              subset=['angular'])


def parse_stops(stationsstr, keep=0):
    _stations = stationsstr.split('-')

    if keep == 1:
        return _stations[:2]
    elif keep == -1:
        return _stations[-2:]
    else:
        return _stations


class SurveyProject:
    def __init__(self,
                 name: str = None,
                 traverse_data: (str, pd.DataFrame) = None,
                 sideshot_data: (str, pd.DataFrame) = None,
                 traverses: (str, pd.DataFrame) = None,
                 known_points: (str, pd.DataFrame) = None,
                 working_dir: (str, Path) = None):

        self.name = name
        self.time = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        self.working_dir = working_dir if working_dir else extract_workind_dir(
            traverses)

        self.t_data = _load(traverse_data)
        self.s_data = _load(sideshot_data)
        self.t_list = _load(traverses)

        self.stations = Container(_load(known_points))
        self.sideshots = Container()

        self.traverses = []
        self.traverses_count = 0
        self.traverses_info = None

        self.computed_sideshots = []
        self.computed_sideshots_count = 0

    @classmethod
    def from_single_file(cls, file):
        _path = Path(file)
        _name = _path.stem
        _all_data = pd.ExcelFile(_path)
        _traverse_data = _all_data.parse('Traverse_Measurements')
        _sideshot_data = _all_data.parse('Taximetrika')
        _traverses = _all_data.parse('Traverses')
        _known_points = _all_data.parse('Known_Points')
        _working_dir = _path.parent

        return cls(name=_name,
                   traverse_data=_traverse_data,
                   sideshot_data=_sideshot_data,
                   traverses=_traverses,
                   known_points=_known_points,
                   working_dir=_working_dir)

    def point2obj(self, points: (list, tuple)) -> List[Point]:
        return [self.stations[points[0]], self.stations[points[1]]]

    def compute_traverses(self):
        self.traverses = []
        for traverse in self.t_list.itertuples():
            if traverse.compute == 1:
                if traverse.t_type == 'LinkTraverse':
                    tr = LinkTraverse(stops=parse_stops(traverse.stations),
                                      data=self.t_data,
                                      start=self.point2obj(
                                          parse_stops(traverse.stations, 1)),
                                      finish=self.point2obj(
                                          parse_stops(traverse.stations, -1)),
                                      working_dir=self.working_dir)
                elif traverse.t_type == 'ClosedTraverse':
                    tr = ClosedTraverse(stops=parse_stops(self.stations),
                                        data=self.t_data,
                                        start=self.point2obj(
                                            parse_stops(traverse.stations, 1)),
                                        working_dir=self.working_dir)
                else:
                    tr = OpenTraverse(stops=parse_stops(traverse.stations),
                                      data=self.t_data,
                                      start=self.point2obj(
                                          parse_stops(traverse.stations, 1)),
                                      working_dir=self.working_dir)

                if tr.is_validated():
                    tr.compute()

                    self.traverses.append(tr)

        if self.traverses:
            self.traverses_info = pd.concat(
                [trav.metrics for trav in self.traverses]).reset_index(
                drop=True)

            self.traverses_info.index = self.traverses_info.index + 1

            self.stations = self.stations + sum(
                [trav.stations for trav in self.traverses])

            self.traverses_count = len(self.traverses)

            return styler(self.traverses_info, traverse_formatter)
        else:
            print("\nNo traverse was computed")

    def export_traverses(self):
        _out = self.working_dir.joinpath('Project_Traverses.xlsx')

        with pd.ExcelWriter(_out) as writer:
            self.traverses_info.round(4).to_excel(writer, sheet_name='Info')

            for i, traverse in enumerate(self.traverses, 1):
                traverse.odeusi.round(4).to_excel(writer,
                                                  index=False,
                                                  sheet_name=str(i))

    def compute_taximetria(self, exclude=None):
        def exclusion(group_check, items):
            if not items:
                return True
            else:
                for i in group_check:
                    if i in items:
                        return False
                return True

        if exclude is None:
            _exclude = []
        else:
            _exclude = exclude

        point_groups = self.s_data.groupby(['station', 'bs'])

        for group in point_groups.groups:
            if group in self.stations and exclusion(group, _exclude):
                _data = point_groups.get_group(group)

                ss = Sideshot(_data,
                              self.stations[group[0]],
                              self.stations[group[1]])

                ss.compute()

                self.computed_sideshots.append(ss)

        if self.computed_sideshots:
            self.sideshots = sum([s.points for s in self.computed_sideshots])
            self.sideshots.sort()
            self.computed_sideshots_count = len(self.sideshots)

        print(f"[{self.computed_sideshots_count}] points were calculated.")
