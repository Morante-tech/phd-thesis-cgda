# -*- coding: utf-8 -*-
"""
@author: smorante
"""

from sklearn.cluster import DBSCAN
import matplotlib.pyplot as plt
import numpy as np

class Dbscan:

    def __init__(self):
        self.db = None
        self.eps = None
        self.min_samples = None
        self.X = None

    def create(self, eps, min_samples):
        self.eps = eps
        self.min_samples = min_samples
        self.db = DBSCAN(self.eps, self.min_samples)
        
        return True

    def fit(self, X):
        self.X=X
        self.db.fit(self.X)
        
        return True
           

    def getOutliers(self):
        return self.db.labels_==-1
        
        
    def plot(self):
        # Black removed and is used for noise instead.
        unique_labels = set(self.db.labels_)
        colors = plt.cm.Spectral(np.linspace(0, 1, len(unique_labels)))
        for k, col in zip(unique_labels, colors):
            if k == -1:
                # Black used for noise.
                col = 'k'
        
            xy = self.X[self.db.labels_ == k]
            plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=col,
                     markeredgecolor='k', markersize=6)
    
        
        plt.show()
