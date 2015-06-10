# -*- coding: utf-8 -*-
"""
Author: Santiago Morante
Robotics Lab. Universidad Carlos III de Madrid
"""
##########################   DTW   ####################################
import libmddtw
import matplotlib.pyplot as plt
from dtw import dtw
##########################   MDS   ####################################
import numpy as np


##########################   DBSCAN   ####################################


import glob
from sklearn import preprocessing

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
    
     ##########################################################################
     ##########################   DTW   ####################################
     ##########################################################################  

    dist=np.zeros((len(demoNames),len(demoNames)))
       
    # fill distance matrix    
    for i in range(len(demoNames)):
        for j in range(len(demoNames)):

            mddtw = libmddtw.Mddtw()
            x,y = mddtw.collapseRows(demons[i],demons[j])
            
#            fig = plt.figure()
#            plt.plot(x)
#            plt.plot(y)
            singleDist, singleCost, singlePath = mddtw.compute(demons[i],demons[j])
            dist[i][j]=singleDist
#            print 'Minimum distance found:', singleDist
#            fig = plt.figure()
#            plt.title(str(i)+","+str(j))
#            plt.imshow(singleCost.T, origin='lower', cmap=plt.cm.gray, interpolation='nearest')
#            plt.plot(singlePath[0], singlePath[1], 'w')
#            plt.xlim((-0.5, singleCost.shape[0]-0.5))
#            plt.ylim((-0.5, singleCost.shape[1]-0.5))
            
#    print "dist", dist
    ###########################################################################
    ###########################   MDS   ####################################
    ###########################################################################

    print "sum", dist.sum(axis=0) / dist.sum(axis=0).sum()
    
    
    
    
     ##########################################################################
     ##########################   DBSCAN   ####################################
     ##########################################################################
#   #  normalize
#    normalizedPoints = normalize(points)
#    
#    #    ########################## dbscan
#    db = libdbscan.Dbscan()
#    db.create(eps=1.5, min_samples=2)
#    db.compute(normalizedPoints)
#    db.plot()
#    print "[INFO] Detected outliers: ", db.getOutliers()
    

##############################################################################
##############################################################################

if __name__ == "__main__":
    main()