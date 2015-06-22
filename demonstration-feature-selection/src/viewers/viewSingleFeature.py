# -*- coding: utf-8 -*-
"""
Author: Santiago Morante
Robotics Lab. Universidad Carlos III de Madrid
"""
################### GENERAL ##############################
from __future__ import division
import glob
from sklearn import preprocessing
import numpy as np

##########################   DTW   ########################
import matplotlib.pyplot as plt
##########################   SUM   #######################

##########################   ZSCORE   ######################
from scipy import stats
#########################################################


SUBFOLDER = "WHOLE_EXPERIMENT" # NONE MINMAX STANDARDIZED WHOLE_EXPERIMENT
NORMALIZATION = "PHYSICAL" # NONE MINMAX STANDARDIZED WHOLE_EXPERIMENT PHYSICAL
EXPERIMENT = "experiment-1"
PATH = "../../datasets/" + EXPERIMENT +"/selected-demonstrations/" + SUBFOLDER +"/*.csv"

def standardize(X):
    return preprocessing.scale(X, axis=0)

def minmaxscale(X):
   min_max_scaler = preprocessing.MinMaxScaler()
   return min_max_scaler.fit_transform(X)

def maxscale_precomputed(X, ranges):
    X_scaled = []
    for elem in X:
        temp= elem/ranges
        X_scaled.append(temp)
    return X_scaled     



def physical_limits(X):
    ranges=np.zeros(([13,2])) # one per feature. minus one because timestamp
    ranges[0] = [500,3000] # x
    ranges[1] = [-2000,2000] # y
    ranges[2] = [-1000,1000] # z
    ranges[3] = [500,3000] # x
    ranges[4] = [-2000,2000] # y
    ranges[5] = [-1000,1000] # z
    ranges[6] = [-2500,2500] # x
    ranges[7] = [-4000,4000] # y
    ranges[8] = [-2000,2000] # z  
    ranges[9] = [0,2500] # x
    ranges[10] = [0,4000] # y
    ranges[11] = [0,2000] # z      
    ranges[12] = [0,5120] # euclidean      
    X_scaled=np.zeros((X.shape )) # one per feature. minus one because timestamp
    for i in range(X.shape[1]): # number of columns
        X_scaled[:,i] = (X[:,i] -  ranges[i,0] ) / ( ranges[i,1] -  ranges[i,0])

  
    return X_scaled    



def get_outlier(points, thresh=2):
    if len(points.shape) == 1:
        points = points[:,None]
    results = stats.zscore(points) 
    return results.flatten() > thresh, results
    
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
                tmp_clean = minmaxscale(tmp_clean)
                demons.append(tmp_clean)
                
    elif NORMALIZATION == "STANDARDIZED":
        ## for demonstration normalization
            for elem in demoNames:
                tmp = np.loadtxt(elem)
                tmp_clean = tmp[:,1:]
                tmp_clean = standardize(tmp_clean)
                demons.append(tmp_clean)     
 
    elif NORMALIZATION == "PHYSICAL":
        ## for demonstration normalization
            for elem in demoNames:
                tmp = np.loadtxt(elem)
                tmp_clean = tmp[:,1:]
                tmp_clean = physical_limits(tmp_clean)
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
            demons=maxscale_precomputed(demons, ranges)
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