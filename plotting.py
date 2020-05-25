# -*- coding: utf-8 -*-
"""
Created on Thu Jan 23 13:38:31 2020

@author: sroy
"""
import matplotlib.pyplot as plt
import openpyxl
import math
import os


def plot(x_values, y_values, x_axis_name, y_axis_name, log_x, log_y, reference_dict):
    list_x = []
    list_y = []
    workbook = openpyxl.Workbook()
    worksheet_name = x_values + "-" + y_values
    workbook.create_sheet(worksheet_name)
    ws = workbook[worksheet_name]
    ws.cell(row=1, column=1, value="Strain")
    ws.cell(row=1, column=2, value="Stress")
    for value in reference_dict.values():
        if y_values in value.keys() and x_values in value.keys():
            list_y.extend(value[y_values])
            list_x.extend(value[x_values])
            for i in range(1, len(list_x)):
                ws.cell(row=i + 1, column=1, value=list_x[i])
                ws.cell(row=i + 1, column=2, value=list_y[i] / math.pow(10, 6))
            workbook.close()
            filepath = os.getcwd() + "/hot_rolling_stress-strain.xlsx"
            workbook.save(filepath)
    plt.plot(list_x, list_y)

    if log_x:
        plt.xscale('log')
    if log_y:
        plt.yscale('log')
    plt.grid(True, which="both", linestyle='--')
    plt.xlabel(x_values)
    plt.ylabel(y_values)
    chart_title = y_axis_name+' vs ' + x_axis_name
    plt.title(chart_title)

    plt.show()
