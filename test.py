# -*- coding: utf-8 -*-
"""
Created on Wed Mar 25 21:03:05 2020

@author: aserafeim
"""
import numpy as np

ar=np.zeros((2,2))
test3=[]
de=0.01
test=[0 ,1]
test2=[1,2]
key=800
dict={'800':100}
print(dict[str(key)])
for i in range(0,10):
    test3.append(i*de)
for j in test:
    print(j)
    ar[j,1]=j
    print(ar)
    