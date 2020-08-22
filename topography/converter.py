# -*- coding: utf-8 -*-
from .computation import *


class NikonRawConverter:
    def __init__(self, file: str = None):
        self.working_dir = infer_working_dir(file)
        self.basename = Path(file).stem
        self.raw = pd.read_csv(file, skiprows=1, names=range(7), header=None)
        self.cleaned = None
        self.staseis = None
        self.taximetrika = None
        self.stats = None
        self.final = None

    def transform(self):
        to_keep = ['OB', 'SS', 'LS', '--Target Generic Prism: "My Prism"',
                   '--Target Reflectorless: "My Reflectorless"']

        df = self.raw[self.raw[0].isin(to_keep)]

        df['midenismos'] = ''
        df['stasi'] = df[1].str.extract('OP([a-zA-Z]+[0-9]+)')[0]
        df['metrisi'] = df[2].str.extract('FP([a-zA-Z0-9]+)')[0]
        df['orizontia'] = df[3].str.extract(r'AR(\d+\.\d+)')[0].astype(float)
        df['katakorifi'] = df[4].str.extract(r'ZE(\d+\.\d+)')[0].astype(float)
        df['apostasi'] = df[5].str.extract(r'SD(\d+\.\d+)')[0].astype(float)
        df['us'] = df[1].str.extract(r'HR:(\d+\.\d+)')[0].astype(float)
        df['uo'] = df[1].str.extract(r'HI(\d+\.\d+)')[0].astype(float)
        df.loc[(df[0] == 'OB') & (df['orizontia'] == 0), 'midenismos'] = df.loc[
            (df[0] == 'OB') & (df['orizontia'] == 0), 'metrisi']

        df2 = df[
            [0, 'midenismos', 'stasi', 'metrisi', 'orizontia', 'katakorifi',
             'apostasi', 'us', 'uo']]

        df2.columns = ['meas_type', 'bs', 'station', 'fs', 'h_angle', 'v_angle',
                       'slope_dist', 'target_h', 'station_h']

        df2['bs'].replace('', np.nan, inplace=True)
        df2['bs'].fillna(method='ffill', inplace=True)

        df2['station_h'].replace(0, np.nan, inplace=True)
        df2['target_h'].replace(0, np.nan, inplace=True)

        df2['station_h'].fillna(method='ffill', inplace=True)
        df2['target_h'].fillna(method='ffill', inplace=True)

        df2['station'].fillna('<NA>', inplace=True)

        self.cleaned = df2.loc[
            df2['station'].str.contains('^[a-zA-Z]+[0-9]+', regex=True)].copy()

        self.cleaned.reset_index(inplace=True, drop=True)

        self.cleaned['meas_type'] = self.cleaned.apply(
            lambda x: meas_type(x['fs'], x['h_angle']), axis=1)

        self.cleaned.loc[self.cleaned['meas_type'] == 'midenismos', 'bs'] = '-'

        indexes_to_delete = []

        search = self.cleaned.loc[
            self.cleaned['meas_type'] == 'midenismos'].copy()

        search.reset_index(inplace=True)

        for i in search.itertuples():
            try:
                if i.station == search.loc[i.Index + 1, 'station'] and i.fs == \
                        search.loc[i.Index + 1, 'fs']:
                    if i.index + 1 == search.loc[i.Index + 1, 'index']:
                        indexes_to_delete.append(i.index)
            except KeyError:
                pass

        self.final = self.cleaned.drop(indexes_to_delete)

        self.staseis = self.final.loc[
            self.cleaned['fs'].str.contains('^[a-zA-Z]+[0-9]+', regex=True)]

        self.taximetrika = self.final.loc[
            self.cleaned['fs'].str.contains(r'^\d+', regex=True)]

        self.stats = self.taximetrika.groupby('station', as_index=False)[
            'fs'].count().sort_values(by='fs')
        self.stats['sunola'] = self.stats['fs'].cumsum()

    def export(self):
        _dir = self.working_dir.joinpath('RAW_Processed')

        if not _dir.exists():
            _dir.mkdir()

        self.cleaned.to_excel(
            _dir.joinpath(f'RAW_{self.basename}_cleaned.xlsx'),
            index=False)

        self.final.to_excel(_dir.joinpath(f'metriseis_{self.basename}.xlsx'),
                            index=False)

        self.staseis.to_excel(_dir.joinpath(f'staseis_{self.basename}.xlsx'),
                              index=False)

        self.taximetrika.to_excel(
            _dir.joinpath(f'taximetrika_{self.basename}.xlsx'), index=False)

        self.stats.to_excel(_dir.joinpath(f'statistics_{self.basename}.xlsx'),
                            index=False)

    class TraverseFormatter:
        def __init__(self, file: str = None):
            self.working_dir = infer_working_dir(file)
            self.basename = Path(file).stem
            self.df = pd.read_excel(file)
            self.final = None
            self.odeusi = None

        def tranform(self):
            self.df.fillna('<NA>', inplace=True)

            self.df['angle'] = self.df.apply(
                lambda x: join_stops_for_angle(x.bs, x.station, x.fs),
                axis=1)

            self.df['dist'] = self.df.apply(
                lambda x: join_stops_for_dist(x['station'], x['fs']), axis=1)

            self.df['stop_dist'] = slope_to_hor(self.df.slope_dist,
                                                self.df.v_angle)

            miki = self.df.groupby('dist')['stop_dist'].mean()

            self.df['h_dist'] = self.df['dist'].map(miki)

            self.df['stop_dh'] = p2p_dh(self.df.slope_dist,
                                        self.df.v_angle,
                                        self.df.station_h,
                                        self.df.target_h)

            self.df['abs_dh'] = abs(self.df['stop_dh'])

            dz = self.df.groupby('dist')['abs_dh'].mean()

            self.df['abs_avg_dh'] = self.df['dist'].map(dz)

            self.df['dz_temp'] = mean_dh_signed(self.df['stop_dh'],
                                                self.df['abs_avg_dh'])

            self.final = self.df[
                ['meas_type', 'bs', 'station', 'fs', 'h_angle', 'v_angle',
                 'slope_dist', 'target_h', 'station_h',
                 'stop_dist', 'stop_dh', 'angle', 'dist', 'h_dist',
                 'abs_avg_dh', 'dz_temp']]

            self.odeusi = self.df.loc[
                self.df['h_angle'] != 0, ['angle', 'dist', 'h_angle', 'h_dist',
                                          'dz_temp', ]].copy()

        def export(self):
            _dir = self.working_dir.joinpath('RAW_Transformed')

            if not _dir.exists():
                _dir.mkdir()

            self.final.to_excel(_dir.joinpath('{self.basename}_Processed.xlsx'),
                                index=False)

            self.odeusi.to_excel(_dir.joinpath('Traverse_Measurements.xlsx'),
                                 index=False)
