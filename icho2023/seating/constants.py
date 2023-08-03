#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   build_interactions.py
@Time    :   2023/07/28 20:48:13
@Author  :   George Trenins
@Contact :   gstrenin@gmail.com
@Desc    :   Construct dictionaries documenting interactions between 
             different countries and store in the data directory
'''


from __future__ import print_function, division, absolute_import
from os import path
import json

# Marker for a "mobile" empty seat. A student may be moved into 
# such a seat over the course of a simulation. Empty seats denoted
# with empty strings '' are considered "blocked" and are not taken
# into account when proposing seating changes.
empty = 'XXX'

# Path to data directory
datadir = path.abspath(__file__)
for i in range(3): datadir = path.dirname(datadir)
datadir = path.join(datadir, "data")


# Aliases, e.g., if instead of a country delegation only individual
# participants have been invited; the corresponding country code
# can then be replaced with user-assigned alpha-3 codes taken
# from the ranges AAA to AAZ, QMA to QZZ, XAA to XZZ, and ZZA to ZZZ
# (https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3#User-assigned_code_elements).
try:
    with open(path.join(datadir, 'aliases.json'), 'r') as f:
        aliases = json.load(f)
except:
    aliases = dict()