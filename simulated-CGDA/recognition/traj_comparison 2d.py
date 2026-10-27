


import os
import pylab as pl
import numpy as np
import matplotlib as mpl
from scipy import linalg


vectorGen   = np.loadtxt(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "unnormalized", "waxGeneralized"))
vectorSim = np.loadtxt(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "waxEvolutionTraj2"), usecols=range(4))  # row 5 of the file has a stray 5th value


# scatter

# traj gen
xGen = vectorGen[:,1:]
yGen = vectorGen[:,1:]

xSim = vectorSim[:,1:]
ySim = vectorSim[:,1:]


# lines
h1= pl.subplot(1, 1, 1)

### temporalmente desordenado para que no se superponga
pl.plot(xGen, yGen, lw=7,color='blue', label='Generalized')
pl.plot(xGen, yGen, 'o', markerfacecolor='blue', markeredgecolor='k', markersize=7)



pl.plot(xSim, ySim, lw=7, color='red', label='Evolutioned')

# points


pl.plot(xSim, ySim, 'o', markerfacecolor='red', markeredgecolor='k', markersize=7)

pl.legend(prop={'size':30})



pl.xticks(np.arange(0.1, 1, 0.1), fontsize=20)
#pl.yticks(np.arange(np.floor(((min(ySim)*0.99)/100))*100,np.ceil( max(ySim)*1.01)+50, 50), fontsize=20)
pl.xlabel('[Normalized Time]', size=30)
#if dimensionTwo==1:
    #pl.ylabel('X [millimeters]', size=30)
#if dimensionTwo==2:
    #pl.ylabel('Y [millimeters]', size=30)
#if dimensionTwo==3:
    #pl.ylabel('Z [millimeters]', size=30)
pl.show()
