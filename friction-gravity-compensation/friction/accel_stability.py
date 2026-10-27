"""
Plot velocity and acceleration over time for the torque recordings of a joint, to check
when the movement becomes stable.

Part of the PhD thesis of Santiago Morante (Robotics Lab, Universidad Carlos III de Madrid).
"""

import matplotlib.pyplot as plt
import numpy as np
import os

#path ="../frictionCompensator/velocities/test3/"
path ="../testTorqueEncs/torques/leftArm/joint22/"

for file in os.listdir(path):
    if file.endswith(".txt"):
        with open(path+file, 'r') as f:
            data = f.readlines()
            time = []
            velocity = []
            for line in data:
                numbers = line.split()
                time.append(float(numbers[1]))
                velocity.append(float(numbers[2]))
            time[:]=[x - time[0] for x in time]
            plt.plot(time, velocity, lw=4)


            accel=[]
            for j in range(len(velocity)-1):
                accel.append( float((velocity[j+1] - velocity[j])/(time[j+1] - time[j])) )
            accel.append(float((velocity[-1] - velocity[-2])/(time[-1] - time[-2])))
            plt.plot(time, accel, lw=4)
            plt.show()


#labels
plt.xlabel('time [s]', size=30)
#plt.ylabel('velocity ' u"\u03C9" ' [rad/s]', size=25)
plt.ylabel('velocity [degrees/s]', size=30)

#limits tuneados a mano
#plt.xlim((0, 1))
plt.xlim((0, 3.5))

plt.xticks(size=25)
#  plt.ylim((100, y))
plt.yticks(size=25)

#plt.title('Velocity vs. Time curves', size=30)

#show
plt.show()
