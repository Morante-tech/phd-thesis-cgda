# -*- coding: utf-8 -*-
"""
@author: smorante
"""

import numpy as np
from dtw import dtw

class Mddtw:

    def create(self):
        return True

    def collapse(self, demo1, demo2, method):

    #    print "Shapes demo1,demo2: ", np.array(demo1).shape, "  , ",  np.array(demo2).shape
        if np.array(demo1).shape[0] > 1 and \
           np.array(demo2).shape[0] > 1 and \
           np.array(demo1).shape[1] == np.array(demo2).shape[1]:
               
               
            if method=="rows":
  #              print "[INFO] Collapsing rows"
                x = np.array(demo1).sum(axis=0)  # zero collaps rows into single row
                y = np.array(demo2).sum(axis=0)
            elif method=="cols":
                
   #             print "[INFO] Collapsing cols"
                x = np.array(demo1).sum(axis=1)  # zero collaps columns into single column
                y = np.array(demo2).sum(axis=1)
            
            else:
                print "[ERROR] Unrecognized method for collapsing!"
                return False
    
            
        elif(np.array(demo1).shape[1] != np.array(demo2).shape[1]):
            print "[ERROR] NumberOfColumns(demo1) != NumberOfColumns(demo2) "
            return False

        else:
  #          print "[INFO] Rows==1, leaving them as they are"

            x = np.array(demo1).flatten()
            y = np.array(demo2).flatten()
             
      #  print "Collapsed demo1: ", x
      #  print "Collapsed demo2: ", y

        return x, y

    
    def compute(self, demo1, demo2):
        dist, cost, path = dtw(demo1, demo2)
        return dist, cost, path

        