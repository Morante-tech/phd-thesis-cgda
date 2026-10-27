"""
Recognition: compare a generalized action with a query (unnormalized data, normalized
here) using Dynamic Time Warping, and plot both.

Part of the PhD thesis of Santiago Morante (Robotics Lab, Universidad Carlos III de Madrid).
"""



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
import pylab as pl

# reading file
actionGeneral="paint"
actionQuery  ="wax"

vectorOne = np.loadtxt("../data/unnormalized/"+actionGeneral+"Generalized")
vectorTwo = np.loadtxt("../data/unnormalized/"+actionQuery+"Query")

if vectorOne.shape[1] != vectorTwo.shape[1]:
    print('VECTOR ONE AND TWO DONT HAVE SAME NUMBER OF COLUMNS (DIMENSIONS)!')

############################################
######## Theoretical Normalization #########
## locX0 locY0 locZ0 area hue sat val angle
############################################

## spatial
## x
#vectorOne[:,1] /= 5000
#vectorTwo[:,1] /= 5000
## y
#vectorOne[:,2] /= 2000
#vectorTwo[:,2] /= 2000
## z
#vectorOne[:,3] /= 2000
#vectorTwo[:,3] /= 2000
## area
#vectorOne[:,4] /= 307200
#vectorTwo[:,4] /= 307200
## hue
#vectorOne[:,5] /= 180
#vectorTwo[:,5] /= 180
## sat
#vectorOne[:,6] /= 255
#vectorTwo[:,6] /= 255
## val
#vectorOne[:,7] /= 255
#vectorTwo[:,7] /= 255
##angle
#vectorOne[:,8] /= 180
#vectorTwo[:,8] /= 180

###########################################
########## DTW all dimensions #############
###########################################

#print 'Number of Dimensions (included time): ', vectorOne.shape[1]
distList =[]
for i in range(1, vectorOne.shape[1]):

    ##scatter plot
    #splot = pl.subplot(1, 1, 1)
    #pl.plot(vectorOne[:,0], vectorOne[:,i], 'o', markerfacecolor='blue', markeredgecolor='k', markersize=5)
    #pl.plot(vectorTwo[:,0], vectorTwo[:,i], 'o', markerfacecolor='red', markeredgecolor='k', markersize=5)
    #pl.title('Dimension ' + str(i), size=20)
    #pl.show()


    #interpolation 1
    minimTime=min(vectorOne[:,0])
    maximTime=max(vectorOne[:,0])
    xi = np.linspace(minimTime, maximTime, 10*len(vectorOne[:,i]))
    testrbfQ = Rbf(vectorOne[:,0], vectorOne[:,i], function='linear')
    yi = testrbfQ(xi)

    pl.subplot(2, 1, 1)
    pl.plot(xi, yi, 'g')
    pl.scatter(vectorOne[:,0], vectorOne[:,i],20, color='blue')
    pl.xticks(())
    #pl.yticks(())
    plt.xlabel(' normalized time', size=25)
    plt.ylabel('feature [units]', size=25)
    pl.title('Generalized', size=20)

    #interpolation 2
    minimTimeQ=min(vectorTwo[:,0])
    maximTimeQ=max(vectorTwo[:,0])
    xiQ = np.linspace(minimTimeQ, maximTimeQ, 10*len(vectorTwo[:,i]))
    testrbfQ = Rbf(vectorTwo[:,0], vectorTwo[:,i], function='linear')
    yiQ = testrbfQ(xiQ)

    pl.subplot(2, 1, 2)
    pl.plot(xiQ, yiQ, 'g')
    pl.scatter(vectorTwo[:,0], vectorTwo[:,i],20, color='blue')
    pl.xticks(())
    #pl.yticks(())
    plt.xlabel(' normalized time', size=25)
    plt.ylabel('feature [units]', size=25)
    pl.title('Query', size=20)

    pl.subplots_adjust(hspace=.8, bottom=0.05)
    pl.show()

#################################################################
    #dtw distance
    dist, px, py, cost = dtw(yi, yiQ)
    distList.extend([dist])
    #print 'Distance (lower, better) for Dim. ', str(i), ' : ', dist

    # plot accumulated cost matrix
    fig = plt.figure(1)
    ax = fig.add_subplot(111)

    plot1 = plt.imshow(cost.T, origin='lower', cmap=cm.gray, interpolation='nearest')
    ax.plot(px, py, color='red', linewidth=3)
    xlim = ax.set_xlim((-0.5, cost.shape[0]-0.5))
    ylim = ax.set_ylim((-0.5, cost.shape[1]-0.5))
    plt.title("Accumulated cost matrix", size=25)
    plt.xlabel('Generalized [samples]', size=25)
    plt.ylabel('Query [samples]', size=25)
    plt.show()

# Total distance
print('Total distance: ', np.sum(distList))
