#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   parse_practical.py
@Time    :   2023/06/24 21:11:46
@Author  :   George Trenins
@Contact :   gstrenin@gmail.com
@Desc    :   None
'''


from __future__ import print_function, division, absolute_import
import numpy as np
import pandas as pd
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--data', default=None, help='Input dataframe to be updated (if any) as a pickle file.')
parser.add_argument('out', help='Output pickle file, augmented with seating data')
args = parser.parse_args()

# Info on seating
roominfo = dict()
for room in 'C191_3 C191_4 E374 E376_1 E376_2 E392 E394_1 E394_2 G194 G196 G198 J190 J192 J194 J196 J198'.split(' '):
    roominfo[f'HCI {room}'] = f'{room}.csv'

# Construct database
studentinfo = {'Code' : [], 'Exam1' : []}

for key in roominfo:
    df = pd.read_csv(roominfo[key],header=None,index_col=None)
    for row in df.columns:
        for col in df.index:
            try:
                col = int(col)
            except ValueError:
                continue
            code = df.at[col,row]
            try:
                skip = np.isnan(code)
            except TypeError:
                skip = False
            if skip : continue
            studentinfo['Code'].append(code)
            studentinfo['Exam1'].append(key)

indices = studentinfo.pop('Code')
df = pd.DataFrame(data = studentinfo, index=indices)
df.index.name = 'Code'
df.sort_index(inplace=True)

if args.data is not None:
    olddf = pd.read_pickle(args.data)
    olddf.sort_index(inplace=True)
    olddf = olddf.join(df)
else:
    olddf = df
olddf.to_pickle(args.out)
print(olddf)

