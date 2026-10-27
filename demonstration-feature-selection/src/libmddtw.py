# -*- coding: utf-8 -*-
"""
@author: smorante

Dynamic Time Warping between demonstrations, using the implementation of the
dmf package. The distance is normalized by the sum of both lengths, as the
`dtw` library used in 2015 did, so the published results can be reproduced.
"""

from dmf import dtw


class Mddtw:

    def create(self):
        return True

    def compute(self, demo1, demo2):
        dist, cost, path = dtw(demo1, demo2, return_path=True)
        return dist / (len(demo1) + len(demo2)), cost, path
