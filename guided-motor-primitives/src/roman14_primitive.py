#!/usr/bin/env python



import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib as mpl
import matplotlib.pyplot as plt
from scipy import linalg
import csv
import codecs
import copy

def comparison(trajOne, trajTwo):
    segmentOne=np.array(trajOne)
    segmentTwo=np.array(trajTwo)

    for i in range(2,5):
        segmentOne[:,i]= segmentOne[:,i] - segmentOne[0,i]
        segmentTwo[:,i]= segmentTwo[:,i] - segmentTwo[0,i]

    dist=0
    for i in range(min(len(trajOne), len(trajTwo))):
        dist = dist + np.linalg.norm(segmentOne[i,2:]-segmentTwo[i,2:])
    return dist

def plotTraj(jointTrajectory):

    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    ax.tick_params(labelsize=28)
    ax.set_xlabel(r"$\Theta_{1}$ [deg]", size=30)
    ax.set_ylabel(r"$\Theta_{2}$ [deg]", size=30)
    ax.set_zlabel(r"$\Theta_{3}$ [deg]", size=30)
   # ax.plot(jointTrajectory[:,2], jointTrajectory[:,3], jointTrajectory[:,4],  lw=2,color='red',label='Human-Guided Random Trajectory')
    ax.plot(jointTrajectory[:,2], jointTrajectory[:,3], jointTrajectory[:,4],  lw=2,color='red',label='Human-Guided Random Trajectory .')
    ax.legend(prop={'size':30})
    plt.show()


def plotDistances(trajOne, trajTwo):
    segmentOne=np.array(trajOne)
    segmentTwo=np.array(trajTwo)

    for i in range(2,5):
        segmentOne[:,i]= segmentOne[:,i] - segmentOne[0,i]
        segmentTwo[:,i]= segmentTwo[:,i] - segmentTwo[0,i]

    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    ax.tick_params(labelsize=30)
    ax.set_xlabel(r"$\Theta_{1}$ [deg]", size=30)
    ax.set_ylabel(r"$\Theta_{2}$ [deg]", size=30)
    ax.set_zlabel(r"$\Theta_{3}$ [deg]", size=30)
    ax.set_xticklabels('')
    ax.set_yticklabels('')
    ax.set_zticklabels('')
    for i in range(len(segmentOne)):
        if i==0:
            ax.plot([segmentOne[i,2], segmentTwo[i,2]],[ segmentOne[i,3], segmentTwo[i,3]], [segmentOne[i,4], segmentTwo[i,4]], lw=2,color='blue',label='Distances')
        else:
            ax.plot([segmentOne[i,2], segmentTwo[i,2]],[ segmentOne[i,3], segmentTwo[i,3]], [segmentOne[i,4], segmentTwo[i,4]], lw=2,color='blue')

    ax.plot(segmentOne[:,2], segmentOne[:,3], segmentOne[:,4],  lw=3,color='red',label='Segment 1')
    ax.plot(segmentTwo[:,2], segmentTwo[:,3], segmentTwo[:,4],  lw=3,color='green',label='Segment 2')
    ax.legend(prop={'size':30})
    plt.show()

def plotSingle(trajOne):
    segmentOne=np.array(trajOne)
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    ax.set_xticklabels('')
    ax.set_yticklabels('')
    ax.set_zticklabels('')
    ax.plot(segmentOne[:,2], segmentOne[:,3], segmentOne[:,4],  lw=5,color='red',label='Segment 1')
    plt.show()

def plot2DXiP():
    x = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160, 170]
    y = [94, 86, 72, 58, 46, 41, 38, 31, 27, 22, 13, 10, 8, 6, 5, 3, 2, 1]
    plt.plot(x, y, linewidth=4)
    plt.ylim([0,94])
    plt.xlim([0,170])

    plt.xlabel("\u03BE", fontsize=30)
    plt.ylabel('Number of Primitives', fontsize=30)
    plt.tick_params(labelsize=25)
    #plt.title('Relation between ' + u'\u03BE' + ' and primitives', fontsize=30)

    plt.grid(True)
    plt.show()


def saveToCSV(primitives, tau, xi):
    fileName='db_var/db_'+ 'tau' +str(tau) + '_xi'+ str(xi)
    # to write in CSV
    with open(fileName, 'wb') as myfile:
        wr = csv.writer(myfile, quoting=csv.QUOTE_MINIMAL)
        for k in range(len(primitives)):
            wr.writerow(primitives[k])

    # to replace '"'
    contents = codecs.open(fileName, encoding='utf-8').read()
    s = contents.replace('"', '')
    with open(fileName, "wb") as f:
        f.write(s.encode("UTF-8"))


def main():

    mpl.rcParams['pdf.fonttype'] = 42
    mpl.rcParams['ps.fonttype'] = 42 # type 42 fonts (truetype) for IEEE papercept system

    #325, 350
    tau=0.5 # length in seconds
    xi=50
    jointTrajectory= np.loadtxt('../../main/app/record/recordedTeo/state/data.log')
    x=list(jointTrajectory)
    plotTraj(jointTrajectory)
    numberOfSlices=0
    realDataMatrix=[]
    slicesList=[]
    temp0=np.array(x).astype('float')

    #slices by time
    newTimeValue= np.ceil(temp0[-1][1] - temp0[0][1])
    numberOfSlices = int(newTimeValue/tau)
    X = np.array(x)
    ## OVERLOAD
    for h in range(numberOfSlices):
        initial=(X.shape[0]/numberOfSlices)*h
        final=(X.shape[0]/numberOfSlices)*(h+1)
        if X[initial:final].shape[0] == 0:
            print('NO POINTS IN THIS SET. PROBABLY NUMBEROFPOINTS < NUMBEROFSLICES')
        else:
            slicesList.append(X[initial:final].tolist())
    plotDistances(slicesList[20],slicesList[50])
    primitives=[]
    primitives.append(slicesList[0])
    for i in range(numberOfSlices):
            for k in range(len(primitives)):
                jay = comparison(slicesList[i],primitives[k])
                if jay < xi:
                    #print 'Similar to primitive', k,'in database. Jay', jay
                    jay=-1
                    break
            if jay !=-1:
                #print 'Adding segment', i,'to database'
                primitives.append(slicesList[i])

    print('xi:', xi)
    print('tau:', tau)
    print('number of primitives:', len(primitives))

    # making a copy to be modified
    relativePrims=copy.deepcopy(primitives)

    # making them relative
    for a in range(len(primitives)):
            for b in range(len(primitives[a])):
                for c in range(2,5):
                    relativePrims[a][b][c]= primitives[a][b][c] - primitives[a][b-1][c]
                    if b==0:
                        relativePrims[a][b][c]= primitives[a][b][c] - primitives[a][0][c]

    #saveToCSV(relativePrims, tau, xi)

if __name__ == '__main__':
	main()
