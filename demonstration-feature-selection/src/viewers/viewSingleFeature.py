# -*- coding: utf-8 -*-
"""
Author: Santiago Morante
Robotics Lab. Universidad Carlos III de Madrid

Plot each feature of the selected demonstrations in its own figure.
"""
################### GENERAL ##############################
import glob
import os
import sys

import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import libtools  # noqa: E402

NORM_FOLDER = "NONE" # NONE MINMAX STANDARDIZED WHOLE-EXPERIMENT PHYSICAL
SUM_FOLDER = "cols" # rows cols
ALPHA_FOLDER = 0.5
EXPERIMENT = "experiment-1"
PATH = os.path.join(HERE, "..", "..", "datasets") + "/" + EXPERIMENT + "/selected-demonstrations/NORM-" + NORM_FOLDER + "/SUM-" + SUM_FOLDER + "/ALPHA-" + str(ALPHA_FOLDER) + "/*.csv"

NORMALIZATION = "PHYSICAL" # NONE MINMAX STANDARDIZED WHOLE-EXPERIMENT PHYSICAL

#################################
def main():

    demoNames = sorted(glob.glob(PATH))
    demons = libtools.normalize(NORMALIZATION,demoNames)

    ##########################   PLOT ##################################

    for f in range(demons[0].shape[1]): # number of columns minus 1 for timestamp
        plt.figure()
        plt.title(str(f+1))
        for i in range(len(demoNames)):
            plt.plot(demons[i][:,f])

    plt.show()

    ####################################################################

if __name__ == "__main__":
    main()
