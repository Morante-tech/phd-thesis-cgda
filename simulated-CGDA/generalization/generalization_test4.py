


from sklearn import mixture, metrics
import pylab as pl
import csv
import numpy as np

# reading file
for action in ['move', 'rotate', 'wax', 'fold', 'paint']:
    numberOfGaussians=0
    actionName=action
    print("Action: ", actionName)
    realDataMatrix=[]
    partialResults=[]
    reader=csv.reader(open("/home/smorante/Repositories/cognitive/xgnitive/main/app/record/recorded3/"+actionName+"_"+str(6)+"/data.log","rb"),delimiter=' ')
    x=list(reader)
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

    print('slices: ', len(partialResults))
    # saving centers
    sortedPoints = sorted(partialResults, key=lambda point: point[0])
    np.savetxt("generalized/"+actionName+"Query", sortedPoints,  fmt='%.14e')


