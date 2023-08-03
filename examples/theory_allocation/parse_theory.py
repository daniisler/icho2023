#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   parse_theory.py
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

# Info on seating and separation into groups
roominfo = {
 'marked_G61_top.csv' : {
    'name' : 'HIL G61',
    'groups' : {
        'I': set([(r,c) for r in 'ABCDEFGH' for c in range(1,5)]),
        'IX': set([(r,c) for r in 'IJKLMN' for c in range(1,5)]),
    }},
 'marked_G61_bottom.csv' : {
    'name' : 'HIL G61',
    'groups' : {
        'V': set([(r,c) for r in 'ABCDEFGH' for c in range(5,9)]),
        'XIII': set([(r,c) for r in 'IJKLMN' for c in range(5,9)]),
    }},
 'marked_G75.csv' : {
    'name' : 'HIL G75',
    'groups' : {
        'II': set([(r,c) for r in 'ABCDEFG' for c in range(1,4)]),
        'VI': set([(r,c) for r in 'ABCDEFG' for c in range(11,14)]),
        'X': set([(r,c) for r in 'HIJ' for c in range(1,7)]).union(
            {('G',4), ('G',5), ('G',6), ('G',7), ('H',7)}
        ),
        'XIV': set([(r,c) for r in 'HIJ' for c in range(8,14)]).union(
            {('I',7), ('J',7), ('G',8), ('G',9), ('G',10)}
        ),
    }},
 'marked_F61_top.csv' : {
    'name' : 'HIL F61',
    'groups' : {
        'III': set([(r,c) for r in 'ABCDEFGH' for c in range(1,5)]),
        'XI': set([(r,c) for r in 'IJKLMN' for c in range(1,5)]),
    }},
 'marked_F61_bottom.csv' : {
    'name' : 'HIL F61',
    'groups' : {
        'VII': set([(r,c) for r in 'ABCDEFGH' for c in range(5,9)]),
        'XV': set([(r,c) for r in 'IJKLMN' for c in range(5,9)]),
    }},
 'marked_F75.csv' : {
    'name' : 'HIL F75',
    'groups' : {
        'IV': set([(r,c) for r in 'ABCDEFG' for c in range(1,4)]),
        'VIII': set([(r,c) for r in 'ABCDEFG' for c in range(11,14)]),
        'XII': set([(r,c) for r in 'HIJ' for c in range(1,7)]).union(
            {('G',4), ('G',5), ('G',6), ('G',7), ('H',7)}
        ),
        'XVI': set([(r,c) for r in 'HIJ' for c in range(8,14)]).union(
            {('I',7), ('J',7), ('G',8), ('G',9), ('G',10)}
        ),
    }},
}

# Construct database
studentinfo = {'Code' : [], 'Exam2' : []}

for key in roominfo:
    df = pd.read_csv(key,index_col=0,skip_blank_lines=True)
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
            for gp in roominfo[key]['groups']:
                hit = (row,col) in roominfo[key]['groups'][gp]
                if hit:
                    break
            hall = roominfo[key]['name']
            if not hit:
                raise KeyError(f'Could not assign theory group to seat{(row, col)} in {hall}')
            studentinfo['Exam2'].append(f'{hall}, Gp. {gp}, {row}{col:02d}')

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
