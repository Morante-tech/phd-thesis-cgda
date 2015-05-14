# -*- coding: utf-8 -*-
"""
Author: Santiago Morante
Robotics Lab. Universidad Carlos III de Madrid
"""


##########################   MDS   ####################################


import numpy as np
from sklearn.metrics import euclidean_distances

import libmds

##########################   DBSCAN   ####################################
import libdbscan
from sklearn.datasets.samples_generator import make_blobs # to create fake points
from sklearn.preprocessing import StandardScaler # to normalize


def normalize(X):
    return StandardScaler().fit_transform(X)


def main():
    


     ##########################################################################
     ##########################   MDS   ####################################
     ##########################################################################
#    # Generate sample data
#    n_samples = 20
#    seed = np.random.RandomState(seed=3)
#    X_true = seed.randint(0, 20, 2 * n_samples).astype(np.float)
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
#    points = md.fit(similarities)
#    md.plot()
    
    
    
    
     ##########################################################################
     ##########################   DBSCAN   ####################################
     ##########################################################################
#    # Generate sample data
#    centers = [[1, 1], [-1, -1], [1, -1]]
#    X, labels_true = make_blobs(n_samples=750, centers=centers, cluster_std=0.4,
#                                random_state=0)
#    
#    # normalize
#    X = normalize(X)
#    
#    db = libdbscan.Dbscan()
#    db.create(eps=0.3, min_samples=10)
#    db.fit(X)
#    db.plot()
    

##############################################################################
##############################################################################

if __name__ == "__main__":
    main()