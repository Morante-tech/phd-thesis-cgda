# -*- coding: utf-8 -*-
"""
Author: Santiago Morante
Robotics Lab. Universidad Carlos III de Madrid
"""
################### GENERAL ##############################
import glob
import numpy as np
import libtools

##########################   DTW   ########################
import libmddtw
###########################################################

NORM_FOLDER = "PHYSICAL" # NONE MINMAX STANDARDIZED WHOLE_EXPERIMENT PHYSICAL
COLLAPSE_FOLDER = "cols" # rows cols
EXPERIMENT = "experiment-1"
PATH = "../datasets/" + EXPERIMENT +"/selected-demonstrations/" + NORM_FOLDER + "/" + COLLAPSE_FOLDER  +"/*.csv"

NORMALIZATION = "PHYSICAL" # NONE MINMAX STANDARDIZED WHOLE_EXPERIMENT PHYSICAL
ALPHA = 1

#################################        
def main():
    
    demoNames = sorted(glob.glob(PATH))
    demons=[]
    demons = libtools.normalize(NORMALIZATION,demoNames)
     
    ##########################   DTW  + SUM #############################

    dist=np.zeros((demons[0].shape[1])) # one per feature. minus one because timestamp
         
    for f in range(demons[0].shape[1]): # number of columns minus 1 for timestamp
        for i in range(len(demoNames)):
            for j in range(len(demoNames)):
    
                mddtw = libmddtw.Mddtw()
                singleDist, singleCost, singlePath = mddtw.compute(demons[i][:,f], demons[j][:,f])
                dist[f]+=singleDist
                print 'Minimum distance found:', singleDist
#               fig = plt.figure()
#         #         plt.title(str(i)+","+str(j))
#               plt.imshow(singleCost.T, origin='lower', cmap=plt.cm.gray, interpolation='nearest')
#               plt.plot(singlePath[0], singlePath[1], 'w')
#               plt.xlim((-0.5, singleCost.shape[0]-0.5))
#               plt.xticks( fontsize=20)
#               plt.ylim((-0.5, singleCost.shape[1]-0.5))
#               plt.yticks( fontsize=20)  
            
    print "[INFO] Feature Dists List: ", dist
        
     ##########################   ZSCORE   #################################
    
    boolzscores, zscores = libtools.get_outlier(dist, thresh=ALPHA)
    print "[INFO] Detected outliers: ", boolzscores, zscores
    
    #####################  PLOT  ###########################################

    libtools.plot_zscores(ALPHA, zscores)

    ########################################################################

if __name__ == "__main__":
    main()