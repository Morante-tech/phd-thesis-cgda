
import matplotlib.pyplot as plt
import numpy as np
import os
import matplotlib.cm as cm

#path ="../frictionCompensator/velocities/test3/"
#path ="../testTorqueEncs/torques/leftArm/joint22/"
path ="../frictionCompensator/velocities/j/"

for file in os.listdir(path):
    if file.endswith(".txt"):
        with open(path+file, 'r') as f:
            data = f.readlines()
            time = []
            velocity = []
            for line in data:
                numbers = line.split()
                time.append(float(numbers[0]))
                velocity.append(float(numbers[1]))
            time[:]=[x - time[0] for x in time]
            plt.plot(time, velocity, lw=4,  c='black')

#labels
plt.xlabel('time [s]', size=30)
#plt.ylabel('velocity ' u"\u03C9" ' [rad/s]', size=25)
plt.ylabel('velocity [degrees/s]', size=30)

#limits tuneados a mano
#plt.xlim((0, 1))
plt.xlim((0, 5))

plt.xticks(size=25)
#  plt.ylim((100, y))
plt.yticks(size=25)

#plt.title('Velocity vs. Time curves', size=30)

#show
plt.show()
