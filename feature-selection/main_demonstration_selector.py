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
from sklearn.metrics import euclidean_distances
import libmds

##########################   DBSCAN   ####################################
import libdbscan
from sklearn.preprocessing import StandardScaler # to normalize

import glob
from sklearn import preprocessing

EXPERIMENT = "experiment1"
PATH = "./datasets/" + EXPERIMENT +"/raw/*.csv"

def normalize(X):
    return StandardScaler().fit_transform(X)

def main():
    
    demons=[]
    demoNames = glob.glob(PATH)
    print demoNames

    for elem in demoNames:
        tmp = np.loadtxt(elem)
        tmp_clean = tmp[:,1:]
        tmp_clean = preprocessing.scale(tmp_clean)
        demons.append(tmp_clean)
    
    dist=np.zeros((len(demoNames),len(demoNames)))
     
     ##########################################################################
     ##########################   DTW   ####################################
     ##########################################################################  


       
    # fill distance matrix    
    for i in range(len(demoNames)):
        for j in range(len(demoNames)):

            mddtw = libmddtw.Mddtw()
            x,y = mddtw.collapseRows(demons[i],demons[j])
            
            #fig = plt.figure()
            #plt.plot(x)
            #plt.plot(y)
            singleDist, singleCost, singlePath = mddtw.compute(demons[i],demons[j])
            dist[i][j]=singleDist
       #     print 'Minimum distance found:', singleDist
            #fig = plt.figure()
        
        #    plt.imshow(cost.T, origin='lower', cmap=plt.cm.gray, interpolation='nearest')
        #    plt.plot(path[0], path[1], 'w')
        #    plt.xlim((-0.5, cost.shape[0]-0.5))
        #    plt.ylim((-0.5, cost.shape[1]-0.5))
            
  #  print "dist", dist
    ###########################################################################
    ###########################   MDS   ####################################
    ###########################################################################

    md = libmds.Mds()
    md.create(n_components=2, metric=False, max_iter=3000, eps=1e-9, random_state=0,
                       dissimilarity="precomputed", n_jobs=-1, n_init=4)

    points = md.compute(dist)
    print "points", points
    md.plot()
    
    
    
    
     ##########################################################################
     ##########################   DBSCAN   ####################################
     ##########################################################################
   #  normalize
    normalizedPoints = normalize(points)
    
    #    ########################## dbscan
    db = libdbscan.Dbscan()
    db.create(eps=1.5, min_samples=2)
    db.compute(normalizedPoints)
    db.plot()
    print "[INFO] Detected outliers: ", db.getOutliers()
    

##############################################################################
##############################################################################

if __name__ == "__main__":
    main()