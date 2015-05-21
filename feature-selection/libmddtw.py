# -*- coding: utf-8 -*-
"""
@author: smorante
"""

import numpy as np
from dtw import dtw

class Mddtw:

    def __init__(self):
        self.x = None
        self.y = None


    def create(self):
        return True

    def collapseRows(self, xRaw, yRaw):
        
        print "Shapes x,y: ", np.array(xRaw).shape, "  , ",  np.array(yRaw).shape
        if np.array(xRaw).shape[0] > 1 and \
           np.array(yRaw).shape[0] > 1 and \
           np.array(xRaw).shape[0] == np.array(yRaw).shape[0]:
               
            print "[INFO] Collapsing rows"
            self.x = np.array(xRaw).sum(axis=0)  # zero collaps rows into single row
            self.y = np.array(yRaw).sum(axis=0)
            
        elif(np.array(xRaw).shape[0] != np.array(yRaw).shape[0]):
            print "[ERROR] NumberOfRows(xRaw) != NumberOfRows(yRaw) "
            return False

        else:
            print "[INFO] Rows==1, leaving them as they are"

            self.x = np.array(xRaw).flatten()
            self.y = np.array(yRaw).flatten()
             
        print "Collapsed X: ", self.x
        print "Collapsed Y: ", self.y

        return self.x, self.y

    
    def compute(self, xRaw, yRaw):
        self.collapseRows(xRaw, yRaw)
        dist, cost, path = dtw(self.x, self.y)
        return dist, cost, path

        