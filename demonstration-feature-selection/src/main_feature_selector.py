# -*- coding: utf-8 -*-
"""
Author: Santiago Morante
Robotics Lab. Universidad Carlos III de Madrid
"""
################### GENERAL ##############################
import glob
from sklearn import preprocessing
import numpy as np

##########################   DTW   ########################
import libmddtw
import matplotlib.pyplot as plt
from dtw import dtw
##########################   SUM   #######################

##########################   ZSCORE   ######################
from scipy import stats
#########################################################


SUBFOLDER = "WHOLE_EXPERIMENT" # NONE MINMAX STANDARDIZED WHOLE_EXPERIMENT
NORMALIZATION = "WHOLE_EXPERIMENT" # NONE MINMAX STANDARDIZED WHOLE_EXPERIMENT
EXPERIMENT = "experiment2"
PATH = "../datasets/" + EXPERIMENT +"/clean/" + SUBFOLDER +"/*.csv"

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



def get_outlier(points, thresh=2):
    if len(points.shape) == 1:
        points = points[:,None]
    results = stats.zscore(points) 
    return results.flatten() > thresh
    
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

    dist=np.zeros((demons[0].shape[1])) # one per feature. minus one because timestamp
         
    for f in range(demons[0].shape[1]): # number of columns minus 1 for timestamp
        for i in range(len(demoNames)):
            for j in range(len(demoNames)):
    
                mddtw = libmddtw.Mddtw()
                singleDist, singleCost, singlePath = mddtw.compute(demons[i][:][f], demons[j][:][f])
              #  print "f,i,j   ;   singleDist, dist[f]: ", f,i,j,singleDist, dist[f]        
                dist[f]+=singleDist
    #            print 'Minimum distance found:', singleDist
    #            fig = plt.figure()
    #            plt.title(str(i)+","+str(j))
    #            plt.imshow(singleCost.T, origin='lower', cmap=plt.cm.gray, interpolation='nearest')
    #            plt.plot(singlePath[0], singlePath[1], 'w')
    #            plt.xlim((-0.5, singleCost.shape[0]-0.5))
    #            plt.ylim((-0.5, singleCost.shape[1]-0.5))
            
    print "[INFO] Feature Dists List: ", dist
        
     #######################################################################
     ##########################   ZSCORE   #################################
     #######################################################################
    
    zscores = get_outlier(dist, thresh=1)
    print "[INFO] Detected outliers: ", zscores
    

##############################################################################
##############################################################################

if __name__ == "__main__":
    main()