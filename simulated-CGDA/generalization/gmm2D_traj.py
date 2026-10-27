"""
2D plot of a Gaussian Mixture Model fitted to the recordings of the wax action, one
component per time slice. Needs demonstration recordings that are not in this
repository.

Part of the PhD thesis of Santiago Morante (Robotics Lab, Universidad Carlos III de Madrid).
"""
print(__doc__)

import itertools

import numpy as np
from scipy import linalg
import pylab as pl
import matplotlib as mpl
import csv


from sklearn import mixture

def inc_avg(currAvg=None, currNumElem=None, newElem=None):

    if not currAvg is None and not currNumElem is None and not newElem is None:
        newAvg = currAvg + (newElem - currAvg) / (currNumElem +1)
        return newAvg
    else:
        raise Exception("inc_avg: something is None")
actionName='wax'
print("Action: ", actionName)
dimOne=1
dimTwo=2
numberOfSlices=0
realDataMatrix=[]
partialResults=[]
partialVariances=[]

for a in range(6):
    reader=csv.reader(open("/home/smorante/Repositories/cognitive/xgnitive/main/app/record/recorded3/"+actionName+"_"+str(a)+"/data.log","rb"),delimiter=' ')
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

## deletes first column (only -1 values) and timestamp
Xnoisy = np.delete(Xnoisy,0,axis=1)
Xnoisy = np.delete(Xnoisy,0,axis=1)

## bad way to delete last 8 columns
for d in range(8):
    Xnoisy = np.delete(Xnoisy,8,axis=1)

#assigning new clean dataset to variable X in numpy array
X = np.array(Xnoisy)

# Fit a mixture of gaussians with EM
best_gmm = mixture.GaussianMixture(n_components=numberOfSlices, covariance_type='full')
best_gmm.fit(X)

clf = best_gmm

print('covar:', clf.covariances_)
# Plot the winner

splot = pl.subplot(1, 1, 1)
Y_ = clf.predict(X)
pl.scatter(X[:, dimOne-1], X[:, dimTwo-1], 3,color='gray')

for i, (mean, covar) in enumerate(zip(clf.means_, clf.covariances_)):
    v, w = linalg.eigh(covar)

    # Plot an ellipse to show the Gaussian component
    angle = np.arctan2(w[0][1], w[0][0])
    angle = 180 * angle / np.pi  # convert to degrees
    v *= 200
    ell = mpl.patches.Ellipse(mean, v[0], v[1], angle=180 + angle, color='blue')
    ell.set_clip_box(splot.bbox)
    ell.set_alpha(.5)
    splot.add_artist(ell)

pl.subplots_adjust(hspace=.35, bottom=.02)
pl.show()


