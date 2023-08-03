#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   add_labels.py
@Time    :   2023/08/03 16:40:11
@Author  :   George Trenins
@Contact :   gstrenin@gmail.com
@Desc    :   Add row and column labels to the raw output of icholocator
'''


from __future__ import print_function, division, absolute_import
import pandas as pd
import numpy as np

alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

# standalone rooms:
for room in ['F75.csv', 'G75.csv']:
    df = pd.read_csv(room, index_col=None, header=None, keep_default_na=False)
    labels = [alphabet[i] for i in range(len(df.columns))]
    df.columns = labels
    df.index = np.arange(1,len(df.index)+1,dtype=int)
    df.to_csv('marked_'+room)

# Half-rooms:
for room in ['F61_top.csv', 'G61_top.csv']:
    df = pd.read_csv(room, index_col=None, header=None, keep_default_na=False)
    labels = [alphabet[i] for i in range(len(df.columns))]
    df.columns = labels[::-1]
    df.index = [1,2,3,4]
    df.to_csv('marked_'+room)
    
for room in ['F61_bottom.csv', 'G61_bottom.csv']:
    df = pd.read_csv(room, index_col=None, header=None, keep_default_na=False)
    labels = [alphabet[i] for i in range(len(df.columns))]
    df.columns = labels[::-1]
    df.index = [5,6,7,8]
    df.to_csv('marked_'+room)
