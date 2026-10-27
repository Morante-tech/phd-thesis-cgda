


import pylab as pl
import matplotlib as mpl
from scipy import linalg

from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np

actionGeneral="wax"
actionQuery  ="wax"

dimensionOne=1
dimensionTwo=2
dimensionThree=3

# reading file

#vectorGen   = np.loadtxt("/home/smorante/Repositories/cognitive/xgnitive/contrib/pendant/packs/ICRA/data/normalized/"+actionGeneral+"Generalized")

vectorZero = np.loadtxt("/home/santi/Repositories/cognitive/xgnitive/main/app/record/recorded3/"+actionGeneral+"_0/data.log")
vectorOne = np.loadtxt("/home/santi/Repositories/cognitive/xgnitive/main/app/record/recorded3/"+actionGeneral+"_1/data.log")
vectorTwo = np.loadtxt("/home/santi/Repositories/cognitive/xgnitive/main/app/record/recorded3/"+actionGeneral+"_2/data.log")
vectorThree = np.loadtxt("/home/santi/Repositories/cognitive/xgnitive/main/app/record/recorded3/"+actionGeneral+"_3/data.log")
vectorFour = np.loadtxt("/home/santi/Repositories/cognitive/xgnitive/main/app/record/recorded3/"+actionGeneral+"_4/data.log")
vectorFive = np.loadtxt("/home/santi/Repositories/cognitive/xgnitive/main/app/record/recorded3/"+actionGeneral+"_5/data.log")
vectorSix = np.loadtxt("/home/santi/Repositories/cognitive/xgnitive/main/app/record/recorded3/"+actionGeneral+"_6/data.log")

###
fig = plt.figure()
ax = fig.add_subplot(projection='3d')


# scatter

# traj gen
xGen = [6.38762472700000e+02,
       6.42391811965000e+02,
       6.80641917184079e+02,
       7.83047694335000e+02,
       8.64809906691542e+02,
       8.16733444044999e+02,
       6.91319608447761e+02,
       6.38455344905001e+02,
       6.36920685935323e+02,]
yGen = [2.72626977500000e+00,
      1.68573559950000e+01,
      8.88397871243782e+01,
      1.20799710345000e+02,
      5.41469797114429e+01,
      -5.19248806450000e+01,
      -6.46731068507463e+01,
      -1.57018014900000e+01,
      3.73245194029851e-01,]
zGen = [-3.97845084999999e+00,
     -3.02628304000000e+00,
     1.23043924875622e+00,
     6.47513742499999e+00,
     7.08611930348259e+00,
    -9.54816400000000e-01,
    -6.88174848258707e+00,
    -4.27471647499999e+00,
    -3.83094820398010e+00]

# traj evol

xEvol = [646.188362, 636.019545, 691.184617, 777.169925, 852.246508, 810.258302, 686.326468, 633.954576, 640.116448]
yEvol = [ -2.141134, 21.391364, 83.792332, 132.174701, 64.744163, -49.713543, -75.613064, -18.500624, -18.684212]
zEvol = [-10.668339, -18.960159, -13.118603, 11.905099, 9.925630, 16.790097, -3.322730, -5.604411, -6.516356]


# traj repet
xZero = vectorZero[:,dimensionOne+1]
yZero = vectorZero[:,dimensionTwo+1]
zZero = vectorZero[:,dimensionThree+1]

xOne = vectorOne[:,dimensionOne+1]
yOne = vectorOne[:,dimensionTwo+1]
zOne = vectorOne[:,dimensionThree+1]

xTwo = vectorTwo[:,dimensionOne+1]
yTwo = vectorTwo[:,dimensionTwo+1]
zTwo = vectorTwo[:,dimensionThree+1]

xThree = vectorThree[:,dimensionOne+1]
yThree = vectorThree[:,dimensionTwo+1]
zThree = vectorThree[:,dimensionThree+1]

xFour = vectorFour[:,dimensionOne+1]
yFour = vectorFour[:,dimensionTwo+1]
zFour = vectorFour[:,dimensionThree+1]

xFive = vectorFive[:,dimensionOne+1]
yFive = vectorFive[:,dimensionTwo+1]
zFive = vectorFive[:,dimensionThree+1]

xSix = vectorSix[:,dimensionOne+1]
ySix = vectorSix[:,dimensionTwo+1]
zSix = vectorSix[:,dimensionThree+1]

# lines

ax.plot(xZero, yZero, zZero,  lw=2,color='black',label='Repetitions')
ax.plot(xOne, yOne, zOne,  lw=2,color='black')
ax.plot(xTwo, yTwo, zTwo,  lw=2,color= 'black')
ax.plot(xThree, yThree, zThree, lw=2,color= 'black')
ax.plot(xFour, yFour, zFour,  lw=2,color='black')
ax.plot(xFive, yFive, zFive, lw=2,color= 'black')
ax.plot(xSix, ySix, zSix,  lw=2,color='black')
ax.plot(xGen, yGen,zGen, lw=7,color='blue', label='Generalized')
ax.plot(xEvol, yEvol, zEvol, lw=7,color='red', label='Evolved')

# points
ax.scatter(xGen, yGen, zGen, s=500,linewidths=1, c='blue')
ax.scatter(xEvol, yEvol, zEvol, s=500,linewidths=1, c='red')


#######
ax.tick_params(labelsize=25)
ax.set_xlabel("X [mm]", size=30)
ax.set_ylabel("Y [mm]", size=30)
ax.set_zlabel("Z [mm]", size=30)
ax.legend(prop={'size':30})
plt.gca().set_zlim(zmin=-100, zmax=100)

plt.show()

