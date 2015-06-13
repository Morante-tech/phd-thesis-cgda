# -*- coding: utf-8 -*-
"""
Author: Juan
Robotics Lab. Universidad Carlos III de Madrid
"""
################### GENERAL ##############################
import glob
from sklearn import preprocessing
import numpy as np
import shutil
import os

import matplotlib as mpl
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import matplotlib.pyplot as plt

EXPERIMENT = "experiment2"
PATH = "/home/teo/git/continuous-goal-directed-actions/feature-selection/datasets/" + EXPERIMENT +"/raw/*.csv"  # sorry (abs path)

#################################        
def main():

    fig = plt.figure()
    ax = fig.gca(projection='3d')
    
    demons=[]
    demoNames = sorted(glob.glob(PATH))

    for elem in demoNames:
	print elem
        tmp = np.loadtxt(elem)
        tmp_clean = tmp[:,1:4]
        #print tmp_clean
        ax.plot(tmp_clean[:,0], tmp_clean[:,1], tmp_clean[:,2], label=elem.split('/')[-1])
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.legend()

    plt.show()

        #demons.append(tmp_clean)

##############################################################################
##############################################################################

if __name__ == "__main__":
    main()
