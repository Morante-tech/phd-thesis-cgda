


from sklearn import mixture, metrics
import pylab as pl
import numpy as np
from dmf import dtw as dmf_dtw


def dtw(x, y):
    """Replacement for mlpy.dtwcore.dtw (mlpy is not available for Python 3).

    Returns (distance, path_x, path_y, cost) like mlpy did, using the DTW of the
    dmf package (Morante-tech/dissimilarity-mapping-filtering).
    """
    dist, cost, (px, py) = dmf_dtw(x, y, return_path=True)
    return dist, px, py, cost
from scipy.interpolate import Rbf, InterpolatedUnivariateSpline
import matplotlib.pyplot as plt
import matplotlib.cm as cm

import yarp


# reading file
def generalization(kinectTrajectory):
    x=list(kinectTrajectory)
    numberOfGaussians=0
    realDataMatrix=[]
    partialResults=[]
    temp0=np.array(x).astype('float')

    #gaussians by time
    newTimeValue= np.ceil(temp0[-1][1] - temp0[0][1])
    numberOfGaussians = int(newTimeValue)
     ## Get the time range and rescale
    r = float(temp0[-1][1] - temp0[0][1])
    temp0[:,1] = [(x - temp0[0][1]) / r for x in temp0[:,1]]

    # append
    realDataMatrix.append(temp0.tolist())

    #test all dimensions and sort (if only 1 traj, not needed)
    Xnoisy = np.vstack(realDataMatrix) # noisy dataset
    #Xnoisy = sorted(Xnoisy, key=lambda column: column[1])

    ## deletes first column (only -1 values)
    Xnoisy = np.delete(Xnoisy,0,axis=1)
    ## bad way to delete last 8 columns
    for d in range(8):
        Xnoisy = np.delete(Xnoisy,9,axis=1)

    #assigning new clean dataset to variable X in numpy array
    X = np.array(Xnoisy)

    ## OVERLOAD
    for h in range(numberOfGaussians):
        #print 'h', h
        #print X.shape[0]
        initial=(X.shape[0]/numberOfGaussians)*h
        final=(X.shape[0]/numberOfGaussians)*(h+1)
        #print X[initial:final].shape
        best_gmm = mixture.GaussianMixture(n_components=1, covariance_type='full')
        best_gmm.fit(X[initial:final])
        #print "Best : ", best_gmm
        #print "Best mean: ", best_gmm.means_.ravel().tolist()
        partialResults.append(best_gmm.means_.ravel().tolist())

    #print 'slices: ', len(partialResults)
    # saving centers
    sortedPoints = sorted(partialResults, key=lambda point: point[0])
    return sortedPoints

def recognition(idealAction, realAction):

    vectorOne=idealAction
    vectorTwo=realAction

    if vectorOne.shape[1] != vectorTwo.shape[1]:
        print('VECTOR ONE AND TWO DONT HAVE SAME NUMBER OF COLUMNS (DIMENSIONS)!')

    ########## DTW all dimensions #############

    #print 'Number of Dimensions (included time): ', vectorOne.shape[1]
    distList =[]
    for i in range(1, vectorOne.shape[1]):

        #interpolation 1
        minimTime=min(vectorOne[:,0])
        maximTime=max(vectorOne[:,0])
        xi = np.linspace(minimTime, maximTime, 10*len(vectorOne[:,i]))
        testrbfQ = Rbf(vectorOne[:,0], vectorOne[:,i], function='linear')
        yi = testrbfQ(xi)

        #interpolation 2
        minimTimeQ=min(vectorTwo[:,0])
        maximTimeQ=max(vectorTwo[:,0])
        xiQ = np.linspace(minimTimeQ, maximTimeQ, 10*len(vectorTwo[:,i]))
        testrbfQ = Rbf(vectorTwo[:,0], vectorTwo[:,i], function='linear')
        yiQ = testrbfQ(xiQ)

        #dtw distance
        dist, px, py, cost = dtw(yi, yiQ)
        distList.extend([dist])
        #print 'Distance (lower, better) for Dim. ', str(i), ' : ', dist
    return np.sum(distList)

def main():

    yarp.Network.init()
    if yarp.Network.checkNetwork() != True:
        print('[fail] found no yarp network (try running "yarpserver &"), bye!')
        quit()
    real_port = yarp.Port()
    ideal_port = yarp.Port()
    output_port = yarp.Port()

    real_port.open("/pythonActionManager")
    ideal_port.open("/idealAction")
    output_port.open("/pythonFitness")

    kinectVector = yarp.Bottle()
    real_port.read(kinectVector) # blocking
    realButGeneralized = generalization(kinectVector)

    idealVector = yarp.Bottle()
    real_port.read(idealVector)

    fitness = recognition(idealVector, realButGeneralized)

    output_port.write(fitness)
    output_port.close()

if __name__ == '__main__':
	main()
