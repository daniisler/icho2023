#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   split_labs.py
@Time    :   2023/08/03 16:53:08
@Author  :   George Trenins
@Contact :   gstrenin@gmail.com
@Desc    :   Split the big E labs into half-labs
'''


from __future__ import print_function, division, absolute_import
import pandas as pd
import numpy as np

for lab in ['E376', 'E394']:
    df = pd.read_csv(lab+'.csv', index_col=None, header=None, keep_default_na=False)
    df1 = df.iloc[:6,:]
    df1.to_csv(lab+"_1.csv", header=False, index=False)
    df2 = df.iloc[6:,:]
    df2.to_csv(lab+"_2.csv", header=False, index=False)