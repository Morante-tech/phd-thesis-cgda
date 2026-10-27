# -*- coding: utf-8 -*-
"""
Author: Santiago Morante
Robotics Lab. Universidad Carlos III de Madrid

Alternative demonstration selector (not used in the paper), on synthetic data:
DTW between demonstrations -> non-metric MDS to 1D -> fit a normal distribution
and print how probable each demonstration is.
"""
import os
import sys

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import libmddtw  # noqa: E402
import libmds  # noqa: E402


def main():

    NUMBER_OF_DEMONSTRATIONS=5
     ##########################################################################
     ##########################   DTW   ####################################
     ##########################################################################

    dist=np.zeros((NUMBER_OF_DEMONSTRATIONS,NUMBER_OF_DEMONSTRATIONS))

    demons=[]

    # fill demonstrations: sine waves of different length and phase, two features each
    # (one row per time step, one column per feature)
    for i in range(NUMBER_OF_DEMONSTRATIONS):
        wave = np.sin(np.arange(15+i)+i)
        demons.append(np.column_stack([wave, wave]))

    # fill distance matrix
    for i in range(NUMBER_OF_DEMONSTRATIONS):
        for j in range(NUMBER_OF_DEMONSTRATIONS):

            mddtw = libmddtw.Mddtw()
            singleDist, singleCost, singlePath = mddtw.compute(demons[i],demons[j])
            dist[i][j]=singleDist

    ###########################################################################
    ###########################   MDS   ####################################
    ###########################################################################

    md = libmds.Mds()
    md.create(n_components=1, metric=False, max_iter=3000, eps=1e-9, random_state=None,
                       dissimilarity="precomputed", n_jobs=1)

    points = md.compute(dist)
    print("points", points.flatten())

     ##########################################################################
     ##########################   norm   ####################################
     ##########################################################################

    param = norm.fit(points.flatten()) # distribution fitting
    x = np.linspace(np.min(points),np.max(points),NUMBER_OF_DEMONSTRATIONS)

    pdf_fitted = norm.pdf(x, loc=param[0],scale=param[1])

    plt.figure()
    plt.title('Normal distribution')
    plt.plot(x,pdf_fitted,'r-')
    plt.hist(points.flatten(),density=True,alpha=.3)
    plt.show()

    for elem in points.flatten():

        if elem <= np.mean(points):
            print("probability of point ", str(elem), ": ", norm.cdf(elem, loc=param[0],scale=param[1]))

        if elem > np.mean(points):
            print("probability of point ", str(elem), ": ", 1-norm.cdf(elem, loc=param[0],scale=param[1]))


##############################################################################
##############################################################################

if __name__ == "__main__":
    main()
