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

    def collapseRows(self, demo1, demo2):
        
        print "Shapes demo1,demo2: ", np.array(demo1).shape, "  , ",  np.array(demo2).shape
        if np.array(demo1).shape[0] > 1 and \
           np.array(demo2).shape[0] > 1 and \
           np.array(demo1).shape[1] == np.array(demo2).shape[1]:
               
            print "[INFO] Collapsing rows"
            self.x = np.array(demo1).sum(axis=0)  # zero collaps rows into single row
            self.y = np.array(demo2).sum(axis=0)
            
        elif(np.array(demo1).shape[1] != np.array(demo2).shape[1]):
            print "[ERROR] NumberOfColumns(demo1) != NumberOfColumns(demo2) "
            return False

        else:
            print "[INFO] Rows==1, leaving them as they are"

            self.x = np.array(demo1).flatten()
            self.y = np.array(demo2).flatten()
             
        print "Collapsed demo1: ", self.x
        print "Collapsed demo2: ", self.y

        return self.x, self.y

    
    def compute(self, demo1, demo2):
        self.collapseRows(demo1, demo2)
        dist, cost, path = dtw(self.x, self.y)
        return dist, cost, path

        