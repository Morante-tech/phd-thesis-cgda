# -*- coding: utf-8 -*-
"""
Author: Juan
Robotics Lab. Universidad Carlos III de Madrid

Plot the 3D trajectories of both objects (red in blue, green in red) for every raw demonstration.
"""
################### GENERAL ##############################
import glob
import os

import numpy as np
import matplotlib.pyplot as plt

EXPERIMENT = "experiment-1"
DATASETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "datasets")
PATH = DATASETS + "/" + EXPERIMENT +"/raw/*.csv"

#################################
def main():

    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')

    demoNames = sorted(glob.glob(PATH))

    for elem in demoNames:
        print(elem)
        tmp = np.loadtxt(elem)
        tmp_clean = tmp[:,1:4]
        tmp_clean2 = tmp[:,4:7]
        ax.plot(tmp_clean[:,0], tmp_clean[:,1], tmp_clean[:,2], c='b')
        ax.plot(tmp_clean2[:,0], tmp_clean2[:,1], tmp_clean2[:,2], c='r')
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')

    plt.show()

##############################################################################
##############################################################################

if __name__ == "__main__":
    main()
