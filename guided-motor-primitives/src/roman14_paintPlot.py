"""
Plot of the RO-MAN 2014 paper: percentage of painted wall over time for the generalized
action and its execution with different numbers of primitives.

Part of the PhD thesis of Santiago Morante (Robotics Lab, Universidad Carlos III de Madrid).
"""
 #from pylab import *
import pylab as pl
import numpy as np
import matplotlib as mpl

def fixedLength():
    t = np.arange(17)
    i1= [0, 6.25, 12.5, 18.75, 25, 31.25, 37.5, 43.75, 50, 56.25, 62.5, 68.75, 75, 81.25, 87.5, 93.75, 100]
    #i2= [0, 6.25, 12.5, 18.75, 25, 31.25, 37.5 , 43.75, 50, 56.25, 62.5, 68.75, 75, 81.25, 87.5, 93.75, 100]
    i3= [0, 6.25, 12.5, 18.75, 25, 31.25, 37.5 , 43.75, 50, 56.25, 62.5, 68.75, 75, 81.25, 87.5, 93.75-6.25, 100-12.5]
    i4= [0, 6.25-6.25, 12.5-12.5, 18.75-18.75, 25-25, 31.25-31.25, 37.5-37.5, 43.75-43.75, 50-50, 56.25-50, 62.5-43.75, 68.75-37.5, 75-43.75, 81.25-50, 87.5-56.25, 93.75-62.5, 100-68.75]
    i5= [0, 6.25, 12.5, 18.75, 25, 31.25, 37.5 , 43.75, 50, 56.25, 62.5, 68.75, 75, 81.25, 87.5, 93.75, 100]
    i6= [0, 6.25, 12.5, 18.75, 25, 31.25, 37.5 , 43.75, 50, 56.25, 62.5, 68.75, 75, 81.25, 87.5, 93.75, 100]
    i7= [0, 6.25, 12.5, 18.75, 25, 31.25-6.25, 37.5-12.5, 43.75-18.75, 50-25, 56.25-31.25, 62.5-37.5, 68.75-43.75, 75-50, 81.25-56.25, 87.5-62.5, 93.75-68.75, 100-75]

    #########
    ax1 = pl.subplot(111)
    pl.scatter(t,i1, color='blue',  alpha=0.7,  s=150)
    ax1.plot(t, i1, 'o-',  linewidth=10,label='Generalized')

    #pl.scatter(t,i2, color='orange',  alpha=0.7, s=20)
    #ax1.plot(t, i2, 'o-', color='orange', label=u'12 prim., $\tau:1$, $d=3$', linewidth=5, alpha=0.7)

    pl.scatter(t,i3, color='red',  alpha=0.7, s=20)
    ax1.plot(t, i3, 'o-', color='red', label='10 primitives', linewidth=6)

    #pl.scatter(t,i6, color='red',  alpha=0.7, s=20)
    #ax1.plot(t, i6, 'o-', color='red', label=u'9 prim.,'+ u"\u03C4"+ '=0.5, d=4', linewidth=6, alpha=0.7)

    pl.scatter(t,i5, color='orange',  alpha=0.7, s=20)
    ax1.plot(t, i5, 'o-', color='orange', label='8 primitives', linewidth=3)

    pl.scatter(t,i4, color='black',  alpha=0.7, s=20)
    ax1.plot(t, i4, 'o-', color='black', label='4 primitives', linewidth=4)

    #pl.scatter(t,i7, color='gray',  alpha=0.7, s=20)
    #ax1.plot(t, i7, 'o-', color='gray', label=u'4 prim.,'+ u"\u03C4"+ '=0.5, d=4', linewidth=4, alpha=0.7)
    ##############

    ax1.set_xlabel('Normalized Time', fontsize=30)
    ax1.set_ylabel('Painted Wall [%]', fontsize=30)

    pl.legend(loc=2, fontsize=30)
    pl.xticks(size=25)
    pl.yticks(size=25)
    pl.ylim([0,100])
    pl.xlim([0,16])

    ##########

    pl.subplots_adjust(hspace=0.4)
    pl.show()

def varLength():
    t = np.arange(17)
    i1= [0, 6.25, 12.5, 18.75, 25, 31.25, 37.5, 43.75, 50, 56.25, 62.5, 68.75, 75, 81.25, 87.5, 93.75, 100]
    i2= [0, 6.25, 12.5, 18.75, 25, 31.25, 37.5 , 43.75, 50, 56.25, 62.5, 68.75, 75, 81.25, 87.5, 93.75, 100]
    i3= [0, 6.25, 12.5, 18.75, 25, 31.25, 37.5 , 43.75, 50, 56.25, 62.5, 68.75, 75, 81.25, 87.5, 93.75, 100]
    i4= [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0]

    #########
    ax1 = pl.subplot(111)
    pl.scatter(t,i1, color='blue',  alpha=0.7,  s=100)
    ax1.plot(t, i1, 'o-',  linewidth=10,label='Generalized', alpha=0.7)

    pl.scatter(t,i2, color='orange',  alpha=0.7, s=20)
    ax1.plot(t, i2, 'o-', color='orange', label='91 primitives', linewidth=5, alpha=0.7)

    pl.scatter(t,i3, color='red',  alpha=0.7, s=20)
    ax1.plot(t, i3, 'o-', color='red', label='33 primitives', linewidth=1, alpha=0.7)

    pl.scatter(t,i4, color='green',  alpha=0.7, s=20)
    ax1.plot(t, i4, 'o-', color='green', label='10 primitives', linewidth=5, alpha=0.7)
    ##############

    ax1.set_xlabel('Normalized Time', fontsize=30)
    ax1.set_ylabel('Painted Wall [%]', fontsize=30)

    pl.legend(loc=2, fontsize=30)
    pl.xticks(size=25)
    pl.yticks(size=25)
    pl.ylim([-0.5,100])
    pl.xlim([0,16])

    ##########

    pl.subplots_adjust(hspace=0.4)
    pl.show()

mpl.rcParams['pdf.fonttype'] = 42
mpl.rcParams['ps.fonttype'] = 42
#varLength()
fixedLength()
