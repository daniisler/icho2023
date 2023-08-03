#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   rooms.py
@Time    :   2023/03/19 18:34:15
@Author  :   George Trenins
@Contact :   gstrenin@gmail.com
@Desc    :   Classes for storing room occupancy plans
'''


from __future__ import print_function, division, absolute_import
import pandas as pd
import numpy as np
from icho2023.seating import constants
import re


class Hall(object):

    _empty_marker = '{:s}-0'.format(constants.empty)
    _blocked_marker = '{:s}-1'.format(constants.empty)

    def __init__(self, name, layout):
        """
        Args:
            name (str): Room label
            layout (str): CSV file with the room layout, wherein
                'XXX-0' indicates available seating and empty string
                means unavailable.
        """

        self.name = name
        self.load(layout)

    def load(self, layout):
        self.array = pd.read_csv(
            layout, header=None, index_col=None, 
            keep_default_na=False).to_numpy(dtype='<U5')
        self.allowed = np.isin(
            self.array, ['', self._blocked_marker], invert=True)
        self.capacity = np.count_nonzero(self.allowed)

    def write(self, name=None):
        if name is None:
            name = '{:s}.csv'.format(self.name.replace(' ', '_'))
        pd.DataFrame(self.array).to_csv(name, header=False, index=False)

    @property
    def occupancy(self):
        return np.count_nonzero(np.isin(
            self.array, 
            ['', self._empty_marker, self._blocked_marker], invert=True))


if __name__ == "__main__":

    from countries import datadir
    from os import path
    layout_input = path.join(datadir, "HIL_061.csv")
    hall0 = Hall("HIL F61", layout_input)
    print(hall0.name, ',', hall0.capacity)
    print(hall0.occupancy)

    layout_input = path.join(datadir, "HIL_075.csv")
    hall1 = Hall("HIL F75", layout_input)
    print(hall1.name, ',', hall1.capacity)
    print(hall1.occupancy)
