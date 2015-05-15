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

#    x = [0, 0, 1, 1, 2, 4, 2, 1, 2, 0]
#    y = [1, 1, 1, 2, 2, 2, 2, 3, 2, 0]


    xRaw = np.matrix([[1, 2, 6, 7, 8],[3, 4, 5, 6, 6]])
    yRaw = np.matrix([[1, 2 , 0, 8, 6],[3, 4, 2 , 7, 5]])

    mddtw= libmddtw.Mddtw()
    x,y = mddtw.collapseRows(xRaw, yRaw)
    
    fig = plt.figure()
    plt.plot(x)
    plt.plot(y)
    dist, cost, path = mddtw.compute(xRaw,yRaw)

    print 'Minimum distance found:', dist
    fig = plt.figure()


    plt.imshow(cost.T, origin='lower', cmap=plt.cm.gray, interpolation='nearest')
    plt.plot(path[0], path[1], 'w')
    plt.xlim((-0.5, cost.shape[0]-0.5))
    plt.ylim((-0.5, cost.shape[1]-0.5))
     ##########################################################################
     ##########################   MDS   ####################################
     ##########################################################################
#    # Generate sample data
#    n_samples = 20
#    seed = np.random.RandomState(seed=3)
#    X_true = seed.randint(0, 10, 2 * n_samples).astype(np.float)
#    X_true = X_true.reshape((n_samples, 2))
#    # Center the data
#    X_true -= X_true.mean()
#    
#    # calculate distances (will be done with dtw)
#    similarities = euclidean_distances(X_true)
#    
#    # Add noise to the similarities
#    noise = np.random.rand(n_samples, n_samples)
#    noise = noise + noise.T
#    noise[np.arange(noise.shape[0]), np.arange(noise.shape[0])] = 0
#    similarities += noise
#    
#    ########################## mds
#    md= libmds.Mds()
#    md.create(n_components=2, metric=False, max_iter=3000, eps=1e-9, random_state=seed,
#                       dissimilarity="precomputed", n_jobs=1)
#
#    points = md.compute(similarities)
#    md.plot()
#    
#    
    
    
     ##########################################################################
     ##########################   DBSCAN   ####################################
     ##########################################################################
    # normalize
#    normalizedPoints = normalize(points)
#    
#    #    ########################## dbscan
#    db = libdbscan.Dbscan()
#    db.create(eps=0.8, min_samples=3)
#    db.compute(normalizedPoints)
#    db.plot()
#    

##############################################################################
##############################################################################

if __name__ == "__main__":
    main()