# -*- coding: utf-8 -*-
"""
Author: Santiago Morante
Robotics Lab. Universidad Carlos III de Madrid
"""

import libdbscan
from sklearn.datasets.samples_generator import make_blobs
from sklearn.preprocessing import StandardScaler


def normalize(X):
    return StandardScaler().fit_transform(X)


def main():
    
     ##############################################################################
    # Generate sample data
    centers = [[1, 1], [-1, -1], [1, -1]]
    X, labels_true = make_blobs(n_samples=750, centers=centers, cluster_std=0.4,
                                random_state=0)
    
    # normalize
    X = normalize(X)
    
    db = libdbscan.Dbscan()
    db.create(eps=0.3, min_samples=10)
    db.fit(X)
    db.plot()
    

##############################################################################
##############################################################################

if __name__ == "__main__":
    main()