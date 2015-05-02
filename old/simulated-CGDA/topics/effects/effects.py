#!/usr/bin/env python

from __future__ import division

from sklearn import mixture, metrics
import pylab as pl
import numpy as np
import mlpy.dtwcore as md
from scipy.interpolate import Rbf, InterpolatedUnivariateSpline
import matplotlib.pyplot as plt
import matplotlib.cm as cm

import time

import yarp


# reading file
def generalization(kinectTrajectory):
    x=list(kinectTrajectory)
    numberOfSlices=0
    realDataMatrix=[]
    partialResults=[]
    temp0=np.array(x).astype('float')

    #slices by time
    newTimeValue= np.ceil(temp0[-1][0] - temp0[0][0])
    numberOfSlices = int(newTimeValue)

     ## Get the time range and rescale
    r = float(temp0[-1][0] - temp0[0][0])
    temp0[:,0] = map(lambda x: (x - temp0[0][0]) / r, temp0[:,0])

    # append
    realDataMatrix.append(temp0.tolist())

    #test all dimensions and sort (if only 1 traj, not needed)
    Xnoisy = np.vstack(realDataMatrix) # noisy dataset
    #Xnoisy = sorted(Xnoisy, key=lambda column: column[1])

    #assigning new clean dataset to variable X in numpy array
    X = np.array(Xnoisy)

    ## OVERLOAD
    for h in range(numberOfSlices):

        initial=(X.shape[0]/numberOfSlices)*h
        final=(X.shape[0]/numberOfSlices)*(h+1)
        if X[initial:final].shape[0] == 0:
            print 'NO POINTS IN THIS SET. PROBABLY NUMBEROFPOINTS < NUMBEROFSLICES'
        if X[initial:final].shape[0] == 1:
            partialResults.append(X[initial:final].ravel().tolist())
        else:
            #best_gmm = mixture.GMM(n_components=1, covariance_type='full')
            #best_gmm.fit(X[initial:final])
            #partialResults.append(best_gmm.means_.ravel().tolist())

            partialResults.append(np.mean(X[initial:final], axis=0))

    # saving centers
    sortedPoints = sorted(partialResults, key=lambda point: point[0])
    return sortedPoints

def recognition(idealAction, realAction):

    vectorOne=np.array(idealAction)
    vectorTwo=np.array(realAction)
    if vectorOne.shape[1] != vectorTwo.shape[1]:
        print 'VECTOR ONE AND TWO DONT HAVE SAME NUMBER OF COLUMNS (DIMENSIONS)!'

    ########## DTW all dimensions #############

    #print 'Number of Dimensions (included time): ', vectorOne.shape[1]
    distList =[]
    for i in range(1, vectorOne.shape[1]):

        #interpolation 1
        minimTime=min(vectorOne[:,0])
        maximTime=max(vectorOne[:,0])
        xi = np.linspace(minimTime, maximTime, 10)
        testrbfQ = Rbf(vectorOne[:,0], vectorOne[:,i], function='linear')
        yi = testrbfQ(xi)

        #interpolation 2
        minimTimeQ=min(vectorTwo[:,0])
        maximTimeQ=max(vectorTwo[:,0])
        xiQ = np.linspace(minimTimeQ, maximTimeQ, 10)
        testrbfQ = Rbf(vectorTwo[:,0], vectorTwo[:,i], function='linear')
        yiQ = testrbfQ(xiQ)

        dist = np.linalg.norm(np.array(yi)-np.array(yiQ))
        distList.extend([dist])
    return np.sum(distList)

class FittingResponder(yarp.PortReader):
    def read(self,connection):
        if not(connection.isValid()):
            print '[fail] FittingResponder connection shutting down.'
            return False
        writer = connection.getWriter()
        if writer==None:
            print '[fail] FittingResponder no one to reply to.'
            return True
        bIn = yarp.Bottle()
        bOut = yarp.Bottle()
        if not( bIn.read(connection) ):
            print '[fail] FittingResponder failed to read input.'
            return False
        #print '[success] Got: ', bIn.toString()
        kinectVector = []
        for external in range(1,bIn.size()):
            internalVector = []
            internalBottle = yarp.Bottle()
            internalBottle.clear()
            internalBottle = bIn.get(external).asList()
            for internal in range(0,internalBottle.size()):
                internalVector.append(internalBottle.get(internal).asDouble())
            kinectVector.append(internalVector)

        realButGeneralized = generalization(kinectVector)

       # idealVector = [[569,638,2,-3],[0,642,16,-3],[0,680,88,1],[0,783,120,6],[1,864,54,7],[1,816,-51,-1],[1,691,-64,-7],[1,638,-15,-4],[1,636,1,-4]]
        idealVector = [[5.69540986509194e-02,6.38762472700000e+02,2.72626977500000e+00,-3.97845084999999e+00],[1.67269023880151e-01,6.42391811965000e+02,1.68573559950000e+01,-3.02628304000000e+00],[2.78900728094060e-01,6.80641917184079e+02,8.88397871243782e+01,1.23043924875622e+00],[3.89203739697794e-01,7.83047694335000e+02,1.20799710345000e+02,6.47513742499999e+00],[5.00745430502879e-01,8.64809906691542e+02,5.41469797114429e+01,7.08611930348259e+00],[6.10441552649295e-01,8.16733444044999e+02,-5.19248806450000e+01,-9.54816400000000e-01],[7.19785184297655e-01,6.91319608447761e+02,-6.46731068507463e+01,-6.88174848258707e+00],[8.29464571628618e-01,6.38455344905001e+02,-1.57018014900000e+01,-4.27471647499999e+00],[9.42920157590202e-01,6.36920685935323e+02,3.73245194029851e-01,-3.83094820398010e+00]]


        idealVector = np.array(idealVector).astype('float')

        fitness = recognition(idealVector, realButGeneralized)
        print fitness

        bOut.addDouble(round(fitness,1))
        return bOut.write(writer)


def main():

    yarp.Network.init()
    if yarp.Network.checkNetwork() != True:
        print '[fail] found no yarp network (try running "yarpserver &"), bye!'
        quit()

    ########################################
    real_port = yarp.Port()
    fittingResponder = FittingResponder()
    #fittingResponder.configure()
    real_port.setReader(fittingResponder)
    real_port.open("/effects:i")
    ########################################

    while True:
        for i in range(0,30):
            #print 'effects will autodestruct in',30-i,'seconds'
            time.sleep(5)
        #print 'Just kidding!'

    ########################################################
    real_port.close()

if __name__ == '__main__':
	main()
