"""
Generalization by time slices of skeleton (kinematic) recordings; saves
generalized/*Generalized kin. Needs demonstration recordings that are not in this
repository.

Part of the PhD thesis of Santiago Morante (Robotics Lab, Universidad Carlos III de Madrid).
"""



from sklearn import mixture, metrics
import pylab as pl
import csv
import numpy as np


def inc_avg(currAvg=None, currNumElem=None, newElem=None):

    if not currAvg is None and not currNumElem is None and not newElem is None:
        newAvg = currAvg + (newElem - currAvg) / (currNumElem +1)
        return newAvg
    else:
        raise Exception("inc_avg: something is None")

# reading file
for action in ['move', 'rotate', 'wax', 'fold', 'paint']:
    numberOfSlices=0
    actionName=action
    print("Action: ", actionName)
    realDataMatrix=[]
    partialResults=[]
    for a in range(6):
        reader=csv.reader(open("/home/smorante/Repositories/cognitive/xgnitive/main/app/record/skeleton/"+actionName+"_"+str(a)+"/data.log","rb"),delimiter=' ')
        x=list(reader)
        temp0=np.array(x).astype('float')

        #gaussians by time
        newTimeValue= np.ceil(temp0[-1][1] - temp0[0][1])
        numberOfSlices = int(inc_avg(numberOfSlices, a, newTimeValue))

        ## Get the time range and rescale
        r = float(temp0[-1][1] - temp0[0][1])
        temp0[:,1] = [(x - temp0[0][1]) / r for x in temp0[:,1]]

        # append
        realDataMatrix.append(temp0.tolist())

    #test all dimensions and sort
    Xnoisy = np.vstack(realDataMatrix) # noisy dataset
    Xnoisy = sorted(Xnoisy, key=lambda column: column[1])

    ## deletes first column (only -1 values)
    Xnoisy = np.delete(Xnoisy,0,axis=1)


    #assigning new clean dataset to variable X in numpy array
    X = np.array(Xnoisy)

    ## OVERLOAD
    for h in range(numberOfSlices):
        #print 'h', h
        #print X.shape[0]
        initial=(X.shape[0]/numberOfSlices)*h
        final=(X.shape[0]/numberOfSlices)*(h+1)
        #print X[initial:final].shape
        best_gmm = mixture.GaussianMixture(n_components=1, covariance_type='full')
        best_gmm.fit(X[initial:final])
        #print "Best : ", best_gmm
        #print "Best mean: ", best_gmm.means_.ravel().tolist()
        partialResults.append(best_gmm.means_.ravel().tolist())

    print('slices: ', len(partialResults))
    # saving centers
    sortedPoints = sorted(partialResults, key=lambda point: point[0])
    np.savetxt("generalized/"+actionName+"Generalized kin", sortedPoints,  fmt='%.14e')

