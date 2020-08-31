# -*- coding: utf-8 -*-

traverse_formatter = {'length': '{:.3f}',
                      'mean_elev': '{:.3f}',
                      'angular': '{:+.4f}',
                      'horizontal': '{:+.3f}',
                      'wx': '{:+.3f}',
                      'wy': '{:+.3f}',
                      'wz': '{:+.3f}'}

point_formatter = {'X': '{:.3f}',
                   'Y': '{:.3f}',
                   'Z': '{:.3f}'}


# def warning(value):
#     color = 'red' if not - 0.1 < value < 0.1 else 'black'
#     return 'color: %s' % color


def color_below_20_red(value):
    if type(value) == type(''):
        return 'color:black'
    else:
        color = 'red' if value <= 20 else 'black'
        return 'color: {}'.format(color)


def warning(s):
    accepted = s.between(-0.1, 0.1)
    return ['color: red' if not v else '' for v in accepted]
