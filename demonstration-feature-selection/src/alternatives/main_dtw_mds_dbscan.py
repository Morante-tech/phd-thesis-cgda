# -*- coding: utf-8 -*-
"""
Author: Santiago Morante
Robotics Lab. Universidad Carlos III de Madrid

Alternative demonstration selector (not used in the paper):
DTW between standardized demonstrations -> MDS to 2D -> DBSCAN, whose noise points are the outliers.
"""
import glob
import os
import sys

import numpy as np
from sklearn import preprocessing
from sklearn.preprocessing import StandardScaler # to normalize

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import libdbscan  # noqa: E402
import libmddtw  # noqa: E402
import libmds  # noqa: E402

EXPERIMENT = "experiment-1"
PATH = os.path.join(HERE, "..", "..", "datasets") + "/" + EXPERIMENT +"/raw/*.csv"

def normalize(X):
    return StandardScaler().fit_transform(X)

def standardize(X):
    return preprocessing.scale(X)

def main():

    demons=[]
    demoNames = sorted(glob.glob(PATH))
    print(demoNames)

    for elem in demoNames:
        tmp = np.loadtxt(elem)
        tmp_clean = tmp[:,1:]
        tmp_clean = standardize(tmp_clean)
        demons.append(tmp_clean)

    dist=np.zeros((len(demoNames),len(demoNames)))

     ##########################################################################
     ##########################   DTW   ####################################
     ##########################################################################

    # fill distance matrix with the multivariate DTW between demonstrations
    for i in range(len(demoNames)):
        for j in range(len(demoNames)):

            mddtw = libmddtw.Mddtw()
            singleDist, singleCost, singlePath = mddtw.compute(demons[i],demons[j])
            dist[i][j]=singleDist

    ###########################################################################
    ###########################   MDS   ####################################
    ###########################################################################

    md = libmds.Mds()
    md.create(n_components=2, metric=True, max_iter=3000, eps=1e-12, random_state=None,
                       dissimilarity="precomputed", n_jobs=-1, n_init=100)

    points = md.compute(dist)
    print("points", points)

     ##########################################################################
     ##########################   DBSCAN   ####################################
     ##########################################################################
    normalizedPoints = normalize(points)

    db = libdbscan.Dbscan()
    db.create(eps=1.5, min_samples=2)
    db.compute(normalizedPoints)
    db.plot()
    print("[INFO] Detected outliers: ", db.getOutliers())


##############################################################################
##############################################################################

if __name__ == "__main__":
    main()
