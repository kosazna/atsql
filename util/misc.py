# -*- coding: utf-8 -*-
import pandas as pd


def column_statistics(data: pd.DataFrame):
    data_dict = {col: {'unique': data[col].value_counts().index.to_list(),
                       'unique_count': len(data[col].unique()),
                       'value_counts': data[col].value_counts()}
                 for col in data.columns if data[col].dtype != 'datetime64[ns]'}

    stats_df = pd.DataFrame.from_dict(data_dict, orient='index',
                                      columns=['unique', 'unique_count',
                                               'value_counts'])

    return stats_df


def dict_to_csv(d, name, columns, directory=None, orient='index'):
    d_frame = pd.DataFrame.from_dict(d, orient=orient, columns=columns[1:])
    d_frame.reset_index(inplace=True)
    d_frame.columns = columns
    d_frame.to_csv(f'{directory}\\' + f'{name}.csv', index=False)
