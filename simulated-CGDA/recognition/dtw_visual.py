
#import numpy as np
#import mlpy.dtwcore as md
#import matplotlib.pyplot as plt
#from matplotlib import cm
#from mpl_toolkits.mplot3d import Axes3D

#fig = plt.figure()
#ax = fig.add_subplot(111, projection='3d')

#dt=0.7
#xr=np.arange(0,4*np.pi,dt)
#x = np.sin(xr)
#y = np.sin((xr+1*np.pi)*.5)
#dist, p1, p2, cost = dtw(x, y)

#cost.tofile("costmatrix.csv", sep=",")

#X = np.arange(0,len(x))
#Y = np.arange(0,len(y))
#X, Y = np.meshgrid(X, Y)

#surf = ax.plot_surface(X, Y, cost, rstride=1, cstride=1, cmap=cm.jet,
                       #linewidth=0, antialiased=False)

#ax.plot( p2, p1, cost[p1,p2], color="red", linewidth=4 )
#plt.show()


from dmf import dtw as dmf_dtw


def dtw(x, y):
    """Replacement for mlpy.dtwcore.dtw (mlpy is not available for Python 3).

    Returns (distance, path_x, path_y, cost) like mlpy did, using the DTW of the
    dmf package (Morante-tech/dissimilarity-mapping-filtering).
    """
    dist, cost, (px, py) = dmf_dtw(x, y, return_path=True)
    return dist, px, py, cost
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.cm as cm

# Data Generation #

# data example 1 #
#x = np.array([[1],[1],[2],[2],[3],[3],[4],[4],[4],[4],[3],[3],[2],[2],[1]])
#y = np.array([[3],[3],[2],[2],[1],[1],[1],[2],[2],[3],[3],[4]])

x = np.array([[0],[0],[0],[1],[1],[2],[3],[3],[2],[1],[1],[0],[0],[0],[0]])
y = np.array([[0],[1],[1],[2],[3],[3],[3],[2],[2],[1],[1],[0],[0],[0],[0]])

#x = np.array([[1],[1], [1]])
#y = np.array([[2],[1], [2]])

# data example 2 #
n_samples = 40
X1 = np.zeros((2))
for i in range(n_samples):
    newrow1 = np.array([i+np.random.random()*40,np.sin(i*np.pi)+np.random.random()/2])
    X1 = np.vstack([X1,newrow1])

X2 = np.zeros((2))
for i in range(n_samples):
    newrow2 = np.array([i+np.random.random()*40,np.sin(i*np.pi/90)+np.random.random()/2])
    X2 = np.vstack([X2,newrow2])

#  Assignation (assign the data generated to two vectors used in calculations) #

vectorOne = X1
vectorTwo = X2

# DTW calculation for each dimension #

print('Dimensions of arrays: ', vectorOne.shape[1])

distList =[]
totalCost=0
for i in range(vectorOne.shape[1]):
    featureOne = vectorOne[:,i]
    featureTwo = vectorTwo[:,i]
    dist, px, py, cost = dtw(featureOne, featureTwo)
    distList.extend([dist])
    print('Distance (lower, better) for Dim. ', str(i), ' : ', dist)
    print('px: ', px)
    print('py: ', py)
    print('Cost Matrix: ')
    print(cost)

    for i in range(len(px)):
        print('Single Cost: ', cost[px[i]][py[i]])
        totalCost=totalCost + cost[px[i]][py[i]]

    print('Total Cost Estimated: ', cost[px[len(px)-1]][py[len(py)-1]] /(cost.shape[0]+cost.shape[1]))
    # plot map of cost #
    fig = plt.figure(1)
    ax = fig.add_subplot(111)
    plot1 = plt.imshow(cost.T, origin='lower', cmap=cm.gray, interpolation='nearest')
    ax.plot(px, py, color='red', linewidth=3)
    xlim = ax.set_xlim((-0.5, cost.shape[0]-0.5))
    ylim = ax.set_ylim((-0.5, cost.shape[1]-0.5))
    plt.xlabel('sequence 2 [samples]', size=25)
    plt.ylabel('sequence 1 [samples]', size=25)
    plt.show()

# Average of distances #
print('List of normalized distances', distList)
print('Averaged distance: ', np.mean(distList))
