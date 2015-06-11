# -*- coding: utf-8 -*-
"""
Author: Santiago Morante
Robotics Lab. Universidad Carlos III de Madrid
"""
################### GENERAL ##############################
import glob
from sklearn import preprocessing
import numpy as np
import shutil
import os

##########################   DTW   ########################
import libmddtw
import matplotlib.pyplot as plt
from dtw import dtw
##########################   SUM   #######################

##########################   ZSCORE   ######################
from scipy import stats
#########################################################



EXPERIMENT = "experiment1"
PATH = "../datasets/" + EXPERIMENT +"/raw/*.csv"

def standardize(X):
    return preprocessing.scale(X, axis=0)

def minmaxscale(X):
   min_max_scaler = preprocessing.MinMaxScaler()
   return min_max_scaler.fit_transform(X)

#def maxscale_precomputed(X, ranges):
#    X_scaled = []
#    for elem in X:
#        temp= elem/ranges
#        X_scaled.append(temp)
#    return X_scaled     

# http://stackoverflow.com/questions/22354094/pythonic-way-of-detecting-outliers-in-one-dimensional-observation-data
#def mad_based_outlier(points, thresh=3.5):
#    if len(points.shape) == 1:
#        points = points[:,None]
#    median = np.median(points, axis=0)
#    diff = np.sum((points - median)**2, axis=-1)
#    diff = np.sqrt(diff)
#    med_abs_deviation = np.median(diff)
#    modified_z_score = 0.6745 * diff / med_abs_deviation
#    return modified_z_score > thresh


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

### for demonstration normalization
    for elem in demoNames:
        tmp = np.loadtxt(elem)
        tmp_clean = tmp[:,1:]
        tmp_clean = minmaxscale(tmp_clean)
        demons.append(tmp_clean)

### for whole experiment normalization
#    demons_temp =[]
#    for elem in demoNames:
#        tmp = np.loadtxt(elem)
#        tmp_clean = tmp[:,1:]
##        tmp_clean = minmaxscale(tmp_clean)
#        demons.append(tmp_clean)
#
#        demons_temp.extend(tmp_clean.tolist())
#    ranges = np.max(np.array(demons_temp), axis=0) 
#    print "ranges", ranges     
#    demons=maxscale_precomputed(demons, ranges)
    
     #######################################################################
     ##########################   DTW   ####################################
     ####################################################################### 

    dist=np.zeros((len(demoNames),len(demoNames)))
       
    # fill distance matrix    
    for i in range(len(demoNames)):
        for j in range(len(demoNames)):

            mddtw = libmddtw.Mddtw()
            x,y = mddtw.collapseRows(demons[i],demons[j])
            
#            fig = plt.figure()
#            plt.plot(x)
#            plt.plot(y)
            singleDist, singleCost, singlePath = mddtw.compute(x,y)
            dist[i][j]=singleDist
#            print 'Minimum distance found:', singleDist
#            fig = plt.figure()
#            plt.title(str(i)+","+str(j))
#            plt.imshow(singleCost.T, origin='lower', cmap=plt.cm.gray, interpolation='nearest')
#            plt.plot(singlePath[0], singlePath[1], 'w')
#            plt.xlim((-0.5, singleCost.shape[0]-0.5))
#            plt.ylim((-0.5, singleCost.shape[1]-0.5))
            
#    print "[INFO] Distance Matrix: ", dist
    ########################################################################
    ###########################   SUM   ####################################
    ########################################################################

    sumDiss = dist.sum(axis=0) / dist.sum(axis=0).sum()
    print "[INFO] Sum of Dissimilarities: ", sumDiss
        
     #######################################################################
     ##########################   ZSCORE   #################################
     #######################################################################
    
    zscores = get_outlier(sumDiss, thresh=1.5)
   # zscores_mad = mad_based_outlier(sumDiss, thresh=10)
    print "[INFO] Detected outliers: ", zscores
    #print "[INFO] Detected outliers MAD: ", zscores_mad
    
    for i in range(len(demoNames)):
        if len(demoNames) != len(zscores):
            print "[ERROR] len(demoNames) != len(zscores): "
            break

        if zscores[i]==False:
            shutil.copy2(demoNames[i], "../datasets/experiment1/clean/" + os.path.basename(demoNames[i]))
            print "[INFO] Copied ", os.path.basename(demoNames[i]), " to clean folder"

##############################################################################
##############################################################################

if __name__ == "__main__":
    main()