# -*- coding: utf-8 -*-
"""
Author: Santiago Morante
Robotics Lab. Universidad Carlos III de Madrid
"""
################### GENERAL ##############################
import glob
from sklearn import preprocessing
import numpy as np
import shutil
import os
import matplotlib.pyplot as plt

##########################   DTW   ########################
import libmddtw
##########################   SUM   #######################

##########################   ZSCORE   ######################
from scipy import stats
#########################################################


NORMALIZATION = "PHYSICAL" # NONE MINMAX STANDARDIZED WHOLE_EXPERIMENT PHYSICAL
EXPERIMENT = "experiment-1"
PATH = "../datasets/" + EXPERIMENT +"/raw/*.csv"
COLLAPSE = "cols" # rows cols
ALPHA = 1

def standardize(X):
    return preprocessing.scale(X, axis=0)

def minmaxscale(X):
   min_max_scaler = preprocessing.MinMaxScaler()
   return min_max_scaler.fit_transform(X)

def maxscale_precomputed(X, ranges):
    X_scaled = []
    for elem in X:
        temp= elem/ranges
        X_scaled.append(temp)
    return X_scaled     

def physical_limits(X):
    ranges=np.zeros(([13,2])) # one per feature. minus one because timestamp
    ranges[0] = [500,3000] # x
    ranges[1] = [-2000,2000] # y
    ranges[2] = [-1000,1000] # z
    ranges[3] = [500,3000] # x
    ranges[4] = [-2000,2000] # y
    ranges[5] = [-1000,1000] # z
    ranges[6] = [-2500,2500] # x
    ranges[7] = [-4000,4000] # y
    ranges[8] = [-2000,2000] # z  
    ranges[9] = [0,2500] # x
    ranges[10] = [0,4000] # y
    ranges[11] = [0,2000] # z      
    ranges[12] = [0,5120] # euclidean      
    X_scaled=np.zeros((X.shape )) # one per feature. minus one because timestamp
    for i in range(X.shape[1]): # number of columns
        X_scaled[:,i] = (X[:,i] -  ranges[i,0] ) / ( ranges[i,1] -  ranges[i,0])
    return X_scaled    


def get_outlier(points, thresh=2):
    if len(points.shape) == 1:
        points = points[:,None]
    results = stats.zscore(points) 
    return results.flatten() > thresh, results
    
#################################        
def main():
    
    demons=[]
    demoNames = sorted(glob.glob(PATH))
#    for elem in demoNames:
#        print elem

    if COLLAPSE=="rows":
        print "[INFO] Collapse: rows"

    elif COLLAPSE=="cols":
        print "[INFO] Collapse: cols"
    else:
        print "[ERROR] Unrecognized method for collapsing!"
        return False


    print "[INFO] Normalization: ", NORMALIZATION

    if NORMALIZATION == "NONE":
        ## for demonstration normalization
            for elem in demoNames:
                tmp = np.loadtxt(elem)
                tmp_clean = tmp[:,1:]
                demons.append(tmp_clean)

    elif NORMALIZATION == "MINMAX":
        ## for demonstration normalization
            for elem in demoNames:
                tmp = np.loadtxt(elem)
                tmp_clean = tmp[:,1:]
                tmp_clean = minmaxscale(tmp_clean)
                demons.append(tmp_clean)
                
    elif NORMALIZATION == "STANDARDIZED":
        ## for demonstration normalization
            for elem in demoNames:
                tmp = np.loadtxt(elem)
                tmp_clean = tmp[:,1:]
                tmp_clean = standardize(tmp_clean)
                demons.append(tmp_clean)     

    elif NORMALIZATION == "PHYSICAL":
        ## for demonstration normalization
            for elem in demoNames:
                tmp = np.loadtxt(elem)
                tmp_clean = tmp[:,1:]
                tmp_clean = physical_limits(tmp_clean)
                demons.append(tmp_clean)  
                
    elif NORMALIZATION == "WHOLE_EXPERIMENT":
        ### for whole experiment normalization
            demons_temp =[]
            for elem in demoNames:
                tmp = np.loadtxt(elem)
                tmp_clean = tmp[:,1:]
                demons.append(tmp_clean)
                demons_temp.extend(tmp_clean.tolist())
            ranges = np.max(np.array(demons_temp), axis=0) 
            print "[INFO] Maximum values per feature: ", ranges     
            demons=maxscale_precomputed(demons, ranges)
    else:
            print "[ERROR] Unrecognized normalization"
            return False

     #######################################################################
     ##########################   DTW   ####################################
     ####################################################################### 

    dist=np.zeros((len(demoNames),len(demoNames)))
       
    # fill distance matrix    
    for i in range(len(demoNames)):
        for j in range(len(demoNames)):

            mddtw = libmddtw.Mddtw()
            x,y = mddtw.collapse(demons[i],demons[j], COLLAPSE)
            
#            fig = plt.figure()
#            plt.plot(x)
#            plt.plot(y)
            singleDist, singleCost, singlePath = mddtw.compute(x,y)
            dist[i][j]=singleDist
#            print 'Minimum distance found:', singleDist
#            fig = plt.figure()
#         #   plt.title(str(i)+","+str(j))
#            plt.imshow(singleCost.T, origin='lower', cmap=plt.cm.gray, interpolation='nearest')
#            plt.plot(singlePath[0], singlePath[1], 'w')
#            plt.xlim((-0.5, singleCost.shape[0]-0.5))
#            plt.xticks( fontsize=20)
#            plt.ylim((-0.5, singleCost.shape[1]-0.5))
#            plt.yticks( fontsize=20)            
#    print "[INFO] Distance Matrix: ", dist
    ########################################################################
    ###########################   SUM   ####################################
    ########################################################################

    sumDiss = dist.sum(axis=0) / dist.sum(axis=0).sum()
    print "[INFO] Sum of Dissimilarities: ", sumDiss
        
     #######################################################################
     ##########################   ZSCORE   #################################
     #######################################################################
    
    boolzscores, zscores  = get_outlier(sumDiss, thresh=ALPHA)
    print "[INFO] Detected outliers: ", boolzscores, zscores

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

##############################################################################


    fig = plt.figure()
    opacity = 0.4
   
    plt.bar(np.arange(len(zscores)), zscores,
                     alpha=opacity,
                     color='b')
    
    plt.xlabel('Demonstration', fontsize=30)
    plt.ylabel('Score', fontsize=30)
    plt.xticks( fontsize=20)
    plt.xlim(0,len(zscores))
    plt.yticks( fontsize=20)
    plt.axhline(y=ALPHA, xmin=0, xmax=1, hold=None, color='red', lw=4, linestyle='--')
    plt.legend()
    plt.tight_layout()
    plt.show()
        


##############################################################################

if __name__ == "__main__":
    main()