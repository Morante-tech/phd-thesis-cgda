# -*- coding: utf-8 -*-
"""
Author: Santiago Morante
Robotics Lab. Universidad Carlos III de Madrid
"""
################### GENERAL ##############################
import glob
import numpy as np
import shutil
import os
import libtools

##########################   DTW   ########################
import libmddtw
#############################################################

NORMALIZATION = "NONE" # NONE MINMAX STANDARDIZED WHOLE_EXPERIMENT PHYSICAL
EXPERIMENT = "experiment-1"
PATH = "../datasets/" + EXPERIMENT +"/raw/*.csv"
COLLAPSE = "cols" # rows cols
ALPHA = 1
SAVE= False
#############################################################
def main():

    if COLLAPSE=="rows":
        print "[INFO] Collapse: rows"

    elif COLLAPSE=="cols":
        print "[INFO] Collapse: cols"
    else:
        print "[ERROR] Unrecognized method for collapsing!"
        return False

    demoNames = sorted(glob.glob(PATH))
    demons=[]
    demons = libtools.normalize(NORMALIZATION,demoNames)

     ##########################   DTW   ##############################

    dist=np.zeros((len(demoNames),len(demoNames)))
       
    # fill distance matrix    
    for i in range(len(demoNames)):
        for j in range(len(demoNames)):

            mddtw = libmddtw.Mddtw()
            x,y = mddtw.collapse(demons[i],demons[j], COLLAPSE)
            singleDist, singleCost, singlePath = mddtw.compute(x,y)
            dist[i][j]=singleDist
            print 'Minimum distance found:', singleDist
#            fig = plt.figure()
#         #   plt.title(str(i)+","+str(j))
#            plt.imshow(singleCost.T, origin='lower', cmap=plt.cm.gray, interpolation='nearest')
#            plt.plot(singlePath[0], singlePath[1], 'w')
#            plt.xlim((-0.5, singleCost.shape[0]-0.5))
#            plt.xticks( fontsize=20)
#            plt.ylim((-0.5, singleCost.shape[1]-0.5))
#            plt.yticks( fontsize=20)            

    ###########################   SUM   ####################################

    sumDiss = dist.sum(axis=0) / dist.sum(axis=0).sum()
    print "[INFO] Sum of Dissimilarities: ", sumDiss
        
     ##########################   ZSCORE   #################################
        
    boolzscores, zscores = libtools.get_outlier(sumDiss, thresh=ALPHA)
    print "[INFO] Detected outliers: ", boolzscores, zscores

    #####################  PLOT  ##########################################

    libtools.plot_zscores(ALPHA, zscores)
    
    ########################  SAVE  ######################################
    
    if SAVE == True:
        if not os.path.exists("../datasets/"+ EXPERIMENT +"/selected-demonstrations/" + NORMALIZATION +"/" + COLLAPSE):
            os.makedirs("../datasets/"+ EXPERIMENT +"/selected-demonstrations/" + NORMALIZATION +"/" + COLLAPSE)
        
        for i in range(len(demoNames)):
            if len(demoNames) != len(zscores):
                print "[ERROR] len(demoNames) != len(zscores): "
                return False
    
            if boolzscores[i]==False:         
                print demoNames[i]
                print "../datasets/"+ EXPERIMENT +"/selected-demonstrations/" + NORMALIZATION +"/" + COLLAPSE +"/" + os.path.basename(demoNames[i])
                shutil.copy2(demoNames[i], "../datasets/"+ EXPERIMENT +"/selected-demonstrations/" + NORMALIZATION +"/" + COLLAPSE +"/" + os.path.basename(demoNames[i]) )
                print "[INFO] Copied ", os.path.basename(demoNames[i]), " to selected-demonstrations folder"
    
    #######################################################################

if __name__ == "__main__":
    main()