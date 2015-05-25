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


def normalize(X):
    return StandardScaler().fit_transform(X)

def main():
    
     ##########################################################################
     ##########################   DTW   ####################################
     ##########################################################################  

    dist=np.zeros((5,5))

    demons=[]
    
    # fill demonstrations
    for i in range(5):
        demons.append(np.matrix([ np.sin(np.arange(15+i)+i)  , np.sin(np.arange(15+i)+i)]))

    
    # fill distance matrix    
    for i in range(5):
        for j in range(5):

            mddtw = libmddtw.Mddtw()
            x,y = mddtw.collapseRows(demons[i],demons[j])
            
            #fig = plt.figure()
            #plt.plot(x)
            #plt.plot(y)
            singleDist, singleCost, singlePath = mddtw.compute(demons[i],demons[j])
            dist[i][j]=singleDist
            print 'Minimum distance found:', singleDist
            #fig = plt.figure()
        
        #    plt.imshow(cost.T, origin='lower', cmap=plt.cm.gray, interpolation='nearest')
        #    plt.plot(path[0], path[1], 'w')
        #    plt.xlim((-0.5, cost.shape[0]-0.5))
        #    plt.ylim((-0.5, cost.shape[1]-0.5))
            
        print "dist", dist
    ###########################################################################
    ###########################   MDS   ####################################
    ###########################################################################

    md = libmds.Mds()
    md.create(n_components=2, metric=False, max_iter=3000, eps=1e-9, random_state=None,
                       dissimilarity="precomputed", n_jobs=1)

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
    

##############################################################################
##############################################################################

if __name__ == "__main__":
    main()