


import itertools
from sklearn import mixture, metrics
from sklearn.cluster import DBSCAN
from scipy import linalg
from scipy.spatial import distance
import pylab as pl
import matplotlib as mpl
from scipy.interpolate import Rbf, InterpolatedUnivariateSpline
import csv
import numpy as np

# reading file
for action in ['wax', 'rotate', 'move', 'fold', 'paint']:
    actionName=action
    print("Action: ", actionName)
    # 6
    reader=csv.reader(open("/home/santi/Repositories/cognitive/xgnitive/main/app/record/recorded3/"+actionName+"_6/data.log","rb"),delimiter=' ')
    x=list(reader)
    temp4=np.array(x).astype('float')
    # Get the time range and rescale
    # change made here
    r = float(temp4[-1][1] - temp4[0][1])
    temp4[:,1] = [(x - temp4[0][1]) / r for x in temp4[:,1]]

    ##normalize (optional)
    #temp4 /= np.max(np.abs(temp4), axis=0)


    ###########################################
    ######## Theoretical Normalization #########
    ## locX0 locY0 locZ0 area hue sat val angle
    ############################################

    ## spatial
     ## x
    #temp4[:,2] /= 5000
     ## y
    #temp4[:,3] /= 2000
     ## z
    #temp4[:,4] /= 2000
    ## area
    #temp4[:,5] /= 307200
    ## hue
    #temp4[:,6] /= 180
    ## sat
    #temp4[:,7] /= 255
    ## val
    #temp4[:,8] /= 255
    ##angle
    #temp4[:,9] /= 180

    ###
    realDataMatrix= np.vstack([temp4])

    # deletes first column (only -1 values)
    realDataMatrix= np.delete(realDataMatrix,0,axis=1)

    ## bad way to delete last 8 columns
    for d in range(8):
        realDataMatrix = np.delete(realDataMatrix,9,axis=1)

    #if: test all dimensions
    Xnoisy = realDataMatrix # noisy dataset
    #Xnoisy = sorted(Xnoisy, key=lambda column: column[1])

    X=[]
    ##else: choose dimensions to be shown (dimOne=time, dimTwo=feature to measure)
    #dimOne = realDataMatrix[:,0]
    #dimTwo = realDataMatrix[:,1]
    #Xnoisy = np.array([dimOne,dimTwo]).T # noisy dataset
    #X=[] # future clean dataset

    # Compute similarities
    D = distance.squareform(distance.pdist(Xnoisy))
    S = 1 - (D / np.max(D))

    # Compute DBSCAN
    db = DBSCAN(eps=0.001, min_samples=10, metric='cosine').fit(S)
    labels = db.labels_

    # Number of clusters in labels, ignoring noise if present.
    n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)

    print('Estimated number of clusters: %d' % n_clusters_)

    # Plotting DBSCAN (but also outlier detection)
    core_samples = db.core_sample_indices_
    unique_labels = set(labels)
    preplot = pl.subplot(4, 1, 1)
    colors = pl.cm.Blues(np.linspace(0, 1, len(unique_labels)))

    outliers=[]
    for k, col in zip(unique_labels, colors):
        class_members = [index[0] for index in np.argwhere(labels == k)]
        cluster_core_samples = [index for index in core_samples
                                if labels[index] == k]
        for index in class_members:
            if index in core_samples and k != -1:
                markersize = 8
                X.append(Xnoisy[index])
                pl.plot(Xnoisy[index][0], Xnoisy[index][1],'o', markerfacecolor=col, markeredgecolor='k', markersize=markersize)
            else:
                markersize = 3
                pl.plot(Xnoisy[index][0], Xnoisy[index][1],'o', markerfacecolor='k', markeredgecolor='k', markersize=markersize)

    if not X:
        X=realDataMatrix  #change here! to avoid null list

    pl.xticks(())
    pl.yticks(())
    pl.title('DBSCAN. Estimated clusters: %d' % n_clusters_, size=20)

    #assigning new clean dataset to variable X in numpy array
    X = np.array(X)

    # Initializing BIC parameters
    lowest_bic = np.inf
    bic = []

    # choose number of clusters to test
    if n_clusters_ <2:
        componentToTest=3
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

    # over loading if compoenents = 1
    print(best_gmm)
    if len(best_gmm.means_)==1:
        best_gmm = mixture.GaussianMixture(n_components=2, covariance_type='full')
        best_gmm.fit(X)

    ## OVERLOAD A ELIMINAR
    #best_gmm = mixture.GaussianMixture(n_components=12, covariance_type='full')
    #best_gmm.fit(X)

    # array of BIC for the graphic table column
    bic = np.array(bic)

    # one tested all components, here we choose the best
    clf = best_gmm
    print("Best result: ", clf)
    print('Means: ', np.round(clf.means_,4))

    ## Plot the BIC scores
    #bars = []
    #spl = pl.subplot(4, 1, 2)

    #xpos = np.array(n_components_range) - 0.1
    #bars.append(pl.bar(xpos, bic[0:len(n_components_range)], width=.2, color='c'))

    #pl.xticks(n_components_range, size=15)
    #pl.yticks(([bic.min() * 1.01 - .01 * bic.max(), bic.max()]), size=12)
    #pl.title('BIC Score', size=20)
    #spl.set_xlabel('Number of components', size=15)

    ## Plot the winner
    #splot = pl.subplot(4, 1, 3)
    #Y_ = clf.predict(X)
    #for i, (mean, covar) in enumerate(zip(clf.means_, clf.covariances_)):
        #v, w = linalg.eigh(covar)
        #if not np.any(Y_ == i):
            #continue
        ##pl.scatter(X[Y_ == i, 0], X[Y_ == i, 1], 8, color='black')
        #pl.plot(X[Y_ == i, 0], X[Y_ == i, 1], 'o', markerfacecolor='black', markeredgecolor='k', markersize=5)

        ## Plot an ellipse to show the Gaussian component
        #angle = np.arctan2(w[0][1], w[0][0])
        #angle = 180 * angle / np.pi  # convert to degrees
        #v *= 4
        #ell = mpl.patches.Ellipse(mean, v[0], v[1], angle=180 + angle, color='b')
        #ell.set_clip_box(splot.bbox)
        #ell.set_alpha(.6)
        #splot.add_artist(ell)

    #pl.xticks(())
    #pl.yticks(())
    #pl.title('GMM-BIC. Components: ' + str(len(clf.means_)), size=20)

    ## saving centers
    sortedPoints = sorted(clf.means_, key=lambda point: point[0])
    np.savetxt("generalized/"+actionName+"Query", sortedPoints,  fmt='%.14e')

    ## plot interpolation
    #meansX, meansY = zip(*clf.means_)

    #if len(meansX) > 1:
        #minimTime=min(meansX)
        #maximTime=max(meansX)

        #print minimTime, maximTime

        #xi = np.linspace(minimTime, maximTime, 10*len(meansX))
        #testrbf = Rbf(meansX, meansY, function='gaussian')
        #yi = testrbf(xi)

        #pl.subplot(4, 1, 4)
        #pl.plot(xi, yi, 'g')
        #pl.scatter(meansX, meansY,20, color='blue')
        #pl.xticks(())
        #pl.yticks(())
        #pl.title('RBF Interpolation', size=20)
        #pl.subplots_adjust(hspace=.8, bottom=0.05)
        #pl.show()

    #else:
        #pl.show()
#
