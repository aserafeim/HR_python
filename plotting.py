# -*- coding: utf-8 -*-
"""
Created on Thu Jan 23 13:38:31 2020

@author: sroy
"""
import matplotlib.pyplot as plt


def plot(x_values, y_values, x_axis_name, y_axis_name, log_x, log_y, reference_dict):
    list_x = []
    list_y = []
    for value in reference_dict.values():
        if y_values in value.keys() and x_values in value.keys():
            list_y.extend(value[y_values])
            list_x.extend(value[x_values])

    plt.plot(list_x, list_y)

    if log_x:
        plt.xscale('log')
    if log_y:
        plt.yscale('log')
    plt.grid(True, which="both", linestyle='--')
    plt.xlabel(x_values)
    plt.ylabel(y_values)
    chart_title = y_axis_name+' vs '+ x_axis_name
    plt.title(chart_title)

    plt.show()
