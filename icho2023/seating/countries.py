#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   countries.py
@Time    :   2023/03/16 21:46:50
@Author  :   George Trenins
@Contact :   gstrenin@gmail.com
@Desc    :   Data on country naming, neighbourhood and compatibility
'''


from __future__ import print_function, division, absolute_import
from os import path
from countryinfo import CountryInfo
import pandas as pd
import copy

# Marker for a "mobile" empty seat. A student may be moved into 
# such a seat over the course of a simulation. Empty seats denoted
# with empty strings '' are considered "blocked" and are not taken
# into account when proposing seating changes.
empty = 'XXX'

# Aliases, e.g., if instead of a country delegation only individual
# participants have been invited; the corresponding country code
# can then be replaced with user-assigned alpha-3 codes taken
# from the ranges AAA to AAZ, QMA to QZZ, XAA to XZZ, and ZZA to ZZZ
# (https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3#User-assigned_code_elements).
aliases = {'RUS':'QMP', 'BLR':'QMC'}

# Path to data directory
datadir = path.abspath(__file__)
for i in range(3): datadir = path.dirname(datadir)
datadir = path.join(datadir, "data")
# Data frame of invitees
inviteframe = pd.read_csv(path.join(datadir, 'invitees.csv'), index_col=0)
inviteframe.index = inviteframe.index.str.lower()
# Dictionary translating official country name to ISO3 code
invitedict = inviteframe['Username'].to_dict()
# Reverse dict, linking country code to an info object
iso3info = dict([(invitedict[key], CountryInfo(key.strip())) for key in invitedict])

# Replace ISO3 codes with aliases whenever appropriate
keys = list(invitedict.keys())
for key in keys:
    val = invitedict.pop(key)
    invitedict.update({key:aliases.get(val, val)})
keys = list(iso3info.keys())
for key in keys:
    val = iso3info.pop(key)
    iso3info.update({aliases.get(key, key): val})

def code(country):
    """Return the three-letter code for the requested country."""

    try:
        return invitedict[country.lower()]
    except KeyError:
        raise KeyError("Unlisted country name '{:s}'".format(country))
    
def add_relation(d, country, *args, coded=False):
    """The input dictionary `d` contains country codes as keys, e.g. 'CHE'.
    The corresponding values are sets of country codes with which the key
    is in a certain relationship. For example, if the relationship is
    language, then the value for 'CHE' might be {'DEU', 'AUT', 'ITA'}.
    We might want to add France (FRA) and Luxembourg (LUX). This function
    ensures that when this is done, the reciprocal relation is also
    recorded ('CHE' is added to the sets associated with 'FRA' and 'LUX')
    
    Args:
        d (dict) : dictionary recording an inter-country relationship
        country (str) : three-letter country code or name of country, for
            which the relationship is augmented
        args : three-letter country codes or names to be added to the
            relationship
        coded (bool, optional) : whether `country` and `args` are given
            as codes. The default is False, in which case it is assumed
            the input is country names, which needs to be translated.
    """
    country_code = country if coded else code(country)
    for c in args:
        # Iterate over countries to be included in the relationship
        arg_code = c if coded else code(c)
        try:
            # Is the relationship already documented?
            listed = arg_code in d[country_code]
        except KeyError:
            # Root country not present in dictionary - add it
            d[country_code] = set()
            listed = False
        if not listed:
            d[country_code] = d[country_code].union(set([arg_code]))
            add_relation(d, arg_code, country_code, coded=True)

# Nearest-neighbour lists (land-only)
nndict = dict()
for key in iso3info:
    neighbours = set(iso3info[key].borders())
    add_relation(nndict, key, *( aliases.get(k, k) for k in neighbours ), coded=True)

# Add non-interacting empty item
nndict[empty] = set()
# Add important sea borders
add_relation(nndict, 'Denmark', 'Norway', 'Sweden')
add_relation(nndict, 'Netherlands', 'Denmark', 'Norway', 'Sweden')
add_relation(nndict, 'Mexico', 'Cuba')
add_relation(nndict, 'Australia', 'New Zealand')
add_relation(nndict, 'Indonesia', 'Malaysia')
add_relation(nndict, 'Singapore', 'Indonesia', 'Malaysia')
add_relation(nndict, 'Philippines', 'Indonesia', 'Malaysia', 'China')
add_relation(nndict, 'Japan', 'Republic of Korea', 'China')
add_relation(nndict, 'India', 'Sri Lanka')
add_relation(nndict, 'Iran', 'Kuwait')
add_relation(nndict, 'Cyprus', 'Turkey', 'Greece', 'Syria', 'Israel')
add_relation(nndict, 'Afghanistan', 'India')
add_relation(nndict, 'China', 'Nepal')
add_relation(nndict, 'China', 'Chinese Taipei')
# Remove spurious relations - Sovereign Base Areas of Akrotiri and Dhekelia
# need not be accounted for
nndict['CYP'].remove('GBR')
nndict['GBR'].remove('CYP')

# Common language lists - make a dictionary of langauges,
# and countries where they are commonly spoken. This 
# list is incomplete, as it only takes account of the
# official language(s) - better results may be achieved by
# using information on spoken languages collected on 
# registration
langdict = dict()
for key in iso3info:
    langs = iso3info[key].languages()
    for lang in langs:
        try:
            langdict[lang].append(key)
        except KeyError:
            langdict[lang] = [key,]

# Remove sets of one
langkeys = list(langdict.keys())
for key in langkeys:
    if len(langdict[key]) == 1:
        langdict.pop(key)

langsets = []
# Keep other sets as is
for key in langdict:
    langsets.append(set(langdict[key]))


# Other interactions, based on https://www.cfr.org/global-conflict-tracker/
# as of May 2023. This is not an expression of a political opinion and must
# not be treated as such. The relations documented here are most prone
# to change and can be modified however the organisers see fit.

other = dict()
add_relation(other, 'Ukraine', 'Russian Federation', 'Belarus')
add_relation(other, 'Syria', 'Turkey')
add_relation(other, 'Israel', 'Iran', 'Kuwait', 'Oman', 'Qatar', 'Saudi Arabia', 
          'Syria', 'United Arab Emirates', 'Afghanistan', 'Bangladesh', 'Indonesia', 'Malaysia', 'Pakistan')
add_relation(other, 'United States of America', 'Iran', 'Afghanistan', 'Cuba')
add_relation(other, 'Saudi Arabia', 'Iran')
add_relation(other, 'Armenia', 'Azerbaijan')
add_relation(other, 'India', 'Pakistan')
add_relation(other, 'China', 'Chinese Taipei')
add_relation(other, 'Turkey', 'Greece', 'Cyprus')

if __name__ == "__main__":

    # Run some quick tests
    for key in invitedict:
        if invitedict[key] != code(key):
            raise ValueError("For {:s}, {:s} != {:s}".format(key, invitedict[key], code(key)))
    print("Country codes:")
    print("Switzerland: ", code('Switzerland'))
    print()
    print("Nearest neighbours:")
    print("Denmark: ", nndict[code('Denmark')])
    print("Kuwait: ", nndict[code('Kuwait')])
    print("Nepal: ", nndict[code('Nepal')])
    print()
    print("Intelligibility sets:")
    for lset in langsets:
        print(lset)
    print()
    print("Other sets:")
    for key in other:
        print(key, other[key])