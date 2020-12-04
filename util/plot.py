# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt


def plt_info(title, xlabel, ylabel, color='k', save_name=''):
    plt.title(title, fontsize=18)
    plt.xlabel(xlabel, fontsize=14, color=color)
    plt.ylabel(ylabel, fontsize=14, color=color)

    plt.savefig(save_name, bbox_inches='tight')
