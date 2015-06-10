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
    return preprocessing.scale(X)

def main():
    
    demons=[]
    demoNames = sorted(glob.glob(PATH))
    for elem in demoNames:
        print elem

    for elem in demoNames:
        tmp = np.loadtxt(elem)
        tmp_clean = tmp[:,1:]
        tmp_clean = standardize(tmp_clean)
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
            
#            fig = plt.figure()
#            plt.plot(x)
#            plt.plot(y)
            singleDist, singleCost, singlePath = mddtw.compute(demons[i],demons[j])
            dist[i][j]=singleDist
#            print 'Minimum distance found:', singleDist
            fig = plt.figure()
            plt.title(str(i)+","+str(j))
            plt.imshow(singleCost.T, origin='lower', cmap=plt.cm.gray, interpolation='nearest')
            plt.plot(singlePath[0], singlePath[1], 'w')
            plt.xlim((-0.5, singleCost.shape[0]-0.5))
            plt.ylim((-0.5, singleCost.shape[1]-0.5))
            
#    print "dist", dist
    ###########################################################################
    ###########################   MDS   ####################################
    ###########################################################################

#    print "sum", dist.sum(axis=0) / dist.sum()
    
    
    
    
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