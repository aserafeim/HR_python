# -*- coding: utf-8 -*-
"""
Created on Wed Mar 25 21:06:45 2020

@author: aserafeim
"""

def error_fun(x_exp,x_sim):
      error=0
      for i in range(len(x_exp)):
                error += (x_exp[i] - x_sim[i]) / x_exp[i]    
      error_final = error/len(x_exp)
      return error_final