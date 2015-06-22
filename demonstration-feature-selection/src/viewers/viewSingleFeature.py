# -*- coding: utf-8 -*-
"""
Author: Santiago Morante
Robotics Lab. Universidad Carlos III de Madrid
"""
################### GENERAL ##############################
from __future__ import division
import glob
import numpy as np
import libtools

##########################   DTW   ########################
import matplotlib.pyplot as plt



NORM_FOLDER = "PHYSICAL" # NONE MINMAX STANDARDIZED WHOLE_EXPERIMENT PHYSICAL
COLLAPSE_FOLDER = "cols" # rows cols
EXPERIMENT = "experiment-1"
PATH = "../../datasets/" + EXPERIMENT +"/selected-demonstrations/" + NORM_FOLDER + "/" + COLLAPSE_FOLDER  +"/*.csv"

NORMALIZATION = "PHYSICAL" # NONE MINMAX STANDARDIZED WHOLE_EXPERIMENT PHYSICAL
  
#################################        
def main():
    
    demons=[]
    demoNames = sorted(glob.glob(PATH))
#    for elem in demoNames:
#        print elem

    print "[INFO] Normalization: ", NORMALIZATION

    if NORMALIZATION == "NONE":
        ## for demonstration normalization
            for elem in demoNames:
                tmp = np.loadtxt(elem)
                tmp_clean = tmp[:,1:]
                demons.append(tmp_clean)

    elif NORMALIZATION == "MINMAX":
        ## for demonstration normalization
            for elem in demoNames:
                tmp = np.loadtxt(elem)
                tmp_clean = tmp[:,1:]
                tmp_clean = libtools.minmaxscale(tmp_clean)
                demons.append(tmp_clean)
                
    elif NORMALIZATION == "STANDARDIZED":
        ## for demonstration normalization
            for elem in demoNames:
                tmp = np.loadtxt(elem)
                tmp_clean = tmp[:,1:]
                tmp_clean = libtools.standardize(tmp_clean)
                demons.append(tmp_clean)     
 
    elif NORMALIZATION == "PHYSICAL":
        ## for demonstration normalization
            for elem in demoNames:
                tmp = np.loadtxt(elem)
                tmp_clean = tmp[:,1:]
                tmp_clean = libtools.physical_limits(tmp_clean)
                demons.append(tmp_clean)  
               
    elif NORMALIZATION == "WHOLE_EXPERIMENT":
        ### for whole experiment normalization
            demons_temp =[]
            for elem in demoNames:
                tmp = np.loadtxt(elem)
                tmp_clean = tmp[:,1:]               
                demons.append(tmp_clean)
                demons_temp.extend(tmp_clean.tolist())
            ranges = np.max(np.array(demons_temp), axis=0) 
          #  print "ranges", ranges     
            demons=libtools.maxscale_precomputed(demons, ranges)
    else:
            print "[ERROR] Unrecognized normalization"
            return False
   
     #######################################################################
     ##########################   DTW  + SUM ####################################
     ####################################################################### 

        
    for f in range(demons[0].shape[1]): # number of columns minus 1 for timestamp
        fig = plt.figure()
        plt.title(str(f+1))
        for i in range(len(demoNames)):
            plt.plot(demons[i][:,f])

            

 

##############################################################################
##############################################################################

if __name__ == "__main__":
    main()