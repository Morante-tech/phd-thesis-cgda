
import numpy as np
import itertools

from sklearn import mixture, metrics
from sklearn.cluster import DBSCAN

from scipy import linalg
from scipy.spatial import distance

import pylab as pl
import matplotlib as mpl

 # ToDo: look for better initial clustering, test with real data

#Generating random sample, in two clusters
n_samples = 30
np.random.seed(0)
C = np.array([[0., 0.91], [1, .4]])
X = np.r_[np.dot(np.random.randn(n_samples, 2), C), np.random.randn(n_samples, 2) + np.array([-6, 3])]

#n_samples = 300
#X = np.zeros((2))
#for i in range(n_samples):
    #newrow = np.array([i+np.random.random()*20,np.sin(i*np.pi/90)+np.random.random()/2])
    #X = np.vstack([X,newrow])

# Normalizing
print("1: ", X)
X /= np.max(np.abs(X), axis=0)
print("2: ", X)

# Checking First-Last point

poX, poY = list(zip(*X))
poMinimX=np.inf
poMaximX=-np.inf

for i in range(len(poX)):
    if poX[i] < poMinimX:
        poMinimX=poX[i]
        yOfMinimX=poY[i]
    if poX[i] > poMaximX:
        poMaximX=poX[i]
        yOfMaximX=poY[i]

print('First point (x = time): ', poMinimX, yOfMinimX)
print('Last point (x = time): ', poMaximX, yOfMaximX)
difX = poMaximX-poMinimX
difY = yOfMaximX-yOfMinimX
redTraj= []
redTraj.append([difX, difY])
print('Diff First-Last: ', redTraj)


# Compute similarities
D = distance.squareform(distance.pdist(X))
S = 1 - (D / np.max(D))

# Compute DBSCAN
db = DBSCAN(eps=0.001, min_samples=10, metric='cosine').fit(S)
labels = db.labels_

# Number of clusters in labels, ignoring noise if present.
n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)

print('Estimated number of clusters: %d' % n_clusters_)

# Initializing parameters
lowest_bic = np.inf
bic = []

# choose number of component to test
componentToTest=2*(n_clusters_ + 1)

print("Maximum components tested: ", componentToTest)
n_components_range = list(range(1, componentToTest+1))

# this is a loop to test every component, choosing the lowest BIC at the end
for n_components in n_components_range:
    # Fit a mixture of gaussians with EM
    gmm = mixture.GaussianMixture(n_components=n_components, covariance_type='full')
    gmm.fit(X)
    bic.append(gmm.bic(X))
    if bic[-1] < lowest_bic:
        lowest_bic = bic[-1]
        best_gmm = gmm

# array of BIC for the graphic table column
bic = np.array(bic)

# one tested all components, here we choose the best
clf = best_gmm
print("Best result: ", clf)
print('Weights: ', np.round(clf.weights_,2))
print('Means: ', np.round(clf.means_,2))
print('Covars: ', np.round(clf.covariances_,2))

# From here, just graphics

# Plot the BIC scores
bars = []
spl = pl.subplot(3, 1, 1)

xpos = np.array(n_components_range) - 0.1
bars.append(pl.bar(xpos, bic[0:len(n_components_range)], width=.2, color='b'))

pl.yticks(())
pl.xticks(n_components_range)
pl.title('BIC Score after Hierarchycal Clustering')
spl.set_xlabel('Number of components')

# Plot the winner
splot = pl.subplot(3, 1, 2)
Y_ = clf.predict(X)
for i, (mean, covar) in enumerate(zip(clf.means_, clf.covariances_)):
    v, w = linalg.eigh(covar)
    if not np.any(Y_ == i):
        continue
    pl.scatter(X[Y_ == i, 0], X[Y_ == i, 1], .8, color='black')

    # Plot an ellipse to show the Gaussian component
    angle = np.arctan2(w[0][1], w[0][0])
    angle = 180 * angle / np.pi  # convert to degrees
    v *= 4
    ell = mpl.patches.Ellipse(mean, v[0], v[1], angle=180 + angle, color='red')
    ell.set_clip_box(splot.bbox)
    ell.set_alpha(.5)
    splot.add_artist(ell)
pl.xticks(())
pl.yticks(())
pl.subplots_adjust(hspace=.55, bottom=.02)
pl.title('GMM-BIC. Gaussians: ' + str(len(clf.means_)))

# interpolation
from scipy.interpolate import Rbf, InterpolatedUnivariateSpline

meansX, meansY = list(zip(*clf.means_))

if len(meansX) > 1:
    minimX=np.inf
    maximX=-np.inf

    for i in range(len(meansX)):
        if meansX[i] < minimX:
            minimX=meansX[i]
        if meansX[i] > maximX:
            maximX=meansX[i]

    #print minimX, maximX

    xi = np.linspace(minimX, maximX, 10*len(meansX))
    testrbf = Rbf(meansX, meansY, function='gaussian')
    yi = testrbf(xi)

    pl.subplot(3, 1, 3)
    pl.plot(xi, yi, 'g')
    pl.scatter(meansX, meansY,8, color='red')
    pl.xticks(())
    pl.yticks(())
    pl.title('Interpolation using RBF')
    pl.subplots_adjust(hspace=.55, bottom=.02)
    pl.show()

else:
    pl.show()
