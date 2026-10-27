"""
Early generalization approach on one recording of the move action, with plots (DBSCAN +
Gaussian Mixture Model). Needs demonstration recordings that are not in this repository.

Part of the PhD thesis of Santiago Morante (Robotics Lab, Universidad Carlos III de Madrid).
"""

import csv
import numpy as np

# reading file
reader=csv.reader(open("/home/smorante/Repositories/cognitive/xgnitive/main/app/record/recorded/move_0/data.log","rb"),delimiter=' ')
x=list(reader)
realDataMatrix=np.array(x).astype('float')

#choose dimensions to be shown (dimOne=time, dimTwo=feature to measure)
dimOne = realDataMatrix[:,1]
dimTwo = realDataMatrix[:,3]
X = np.array([dimOne,dimTwo]).T
#print X

import itertools

from sklearn import mixture, metrics
from sklearn.cluster import DBSCAN

from scipy import linalg
from scipy.spatial import distance

import pylab as pl
import matplotlib as mpl


# Normalizing
#print "1: ", np.round(X,5)

X /= np.max(np.abs(X), axis=0)
#print "2: ", np.round(X,5)

# Compute similarities
D = distance.squareform(distance.pdist(X))
S = 1 - (D / np.max(D))

# Compute DBSCAN
db = DBSCAN(eps=0.001, min_samples=5, metric='cosine').fit(S)
labels = db.labels_

# Number of clusters in labels, ignoring noise if present.
n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)

print('Estimated number of clusters: %d' % n_clusters_)

# Plotting DBSCAN
# Black removed and is used for noise instead.
core_samples = db.core_sample_indices_
unique_labels = set(labels)

preplot = pl.subplot(4, 1, 1)

colors = pl.cm.Blues(np.linspace(0, 1, len(unique_labels)))

for k, col in zip(unique_labels, colors):
    if k == -1:
        # Black used for noise.
        col = 'k'
        markersize = 5
    class_members = [index[0] for index in np.argwhere(labels == k)]
    cluster_core_samples = [index for index in core_samples
                            if labels[index] == k]
    for index in class_members:
        x = X[index]
        if index in core_samples and k != -1:
            markersize = 8
        else:
            markersize = 3
        pl.plot(x[0], x[1], 'o', markerfacecolor=col,
                markeredgecolor='k', markersize=markersize)

pl.xticks(())
pl.yticks(())

pl.title('DBSCAN. Estimated clusters: %d' % n_clusters_, size=20)

# Initializing BIC parameters
lowest_bic = np.inf
bic = []

# choose number of component to test
if n_clusters_ ==0:
    componentToTest=2
else:
    componentToTest=2*n_clusters_

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


# Plot the BIC scores
bars = []
spl = pl.subplot(4, 1, 2)

xpos = np.array(n_components_range) - 0.1
bars.append(pl.bar(xpos, bic[0:len(n_components_range)], width=.2, color='c'))

pl.xticks(n_components_range, size=15)
pl.yticks(([bic.min() * 1.01 - .01 * bic.max(), bic.max()]), size=12)
pl.title('BIC Score', size=20)
spl.set_xlabel('Number of components', size=15)

# Plot the winner
splot = pl.subplot(4, 1, 3)
Y_ = clf.predict(X)
for i, (mean, covar) in enumerate(zip(clf.means_, clf.covariances_)):
    v, w = linalg.eigh(covar)
    if not np.any(Y_ == i):
        continue
    #pl.scatter(X[Y_ == i, 0], X[Y_ == i, 1], 8, color='black')
    pl.plot(X[Y_ == i, 0], X[Y_ == i, 1], 'o', markerfacecolor='black', markeredgecolor='k', markersize=5)


    # Plot an ellipse to show the Gaussian component
    angle = np.arctan2(w[0][1], w[0][0])
    angle = 180 * angle / np.pi  # convert to degrees
    v *= 4
    ell = mpl.patches.Ellipse(mean, v[0], v[1], angle=180 + angle, color='b')
    ell.set_clip_box(splot.bbox)
    ell.set_alpha(.6)
    splot.add_artist(ell)


pl.xticks(())
pl.yticks(())
pl.title('GMM-BIC. Components: ' + str(len(clf.means_)), size=20)

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

    print(minimX, maximX)

    xi = np.linspace(minimX, maximX, 10*len(meansX))
    testrbf = Rbf(meansX, meansY, function='gaussian')
    yi = testrbf(xi)


    pl.subplot(4, 1, 4)
    pl.plot(xi, yi, 'g')
    pl.scatter(meansX, meansY,20, color='blue')
    pl.xticks(())
    pl.yticks(())
    pl.title('RBF Interpolation', size=20)
    pl.subplots_adjust(hspace=.8, bottom=0.05)
    pl.show()

else:
    pl.show()
