# -*- coding: utf-8 -*-
"""
Created on Thu Jan 23 13:38:31 2020

@author: sroy
"""
# from main import main_dict
import matplotlib.pyplot as plt

# def plot_func(xvalues, yvalues, x_axis_name, y_axis_name, log_x, log_y, ref_dict):
#
# #    total_temp_list, real_time = [], []
#     temp_x, temp_y = xvalues, yvalues
#
# # =============================================================================
# #     for key, val in ref_dict.items():
# # # =============================================================================
# # #         total_temp_list += val['temperature_list']
# # #         real_time += val['global_time']
# # # =============================================================================
# #         if xvalues in key and yvalues in key:
# #             temp_x.extend(val[xvalues])
# #             temp_y.extend(val[yvalues])
# # =============================================================================
# # =============================================================================
# #     if xvalues in ref_dict and yvalues in ref_dict:
# #         temp_x.extend(ref_dict[xvalues])
# #         temp_y.extend(ref_dict[yvalues])
# # =============================================================================
#
#     plt.plot(temp_x, temp_y, 'r')
#
#     if log_x == True:
#         plt.xscale('log')
#     if log_y == True:
#         plt.yscale('log')
#     plt.grid(True, which="both", linestyle='--')
#     plt.xlabel(x_axis_name)
#     plt.ylabel(y_axis_name)
#     chart_title = y_axis_name+' vs '+ x_axis_name
#     plt.title(chart_title)
#
#     plt.show()


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
