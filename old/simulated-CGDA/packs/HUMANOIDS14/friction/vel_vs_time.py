
import matplotlib.pyplot as plt
import numpy as np

# vectors data
torque = []
time = []
velocity = []

jointName="22"
current = "1.35"

# file
with open("../testTorqueEncs/torques/leftArm/joint" + jointName + "/torque_" + current +".txt", 'r') as f:
    data = f.readlines()
    for line in data:
        numbers = line.split()
        torque.append(float(numbers[0]))
        time.append(float(numbers[1]))
        velocity.append(float(numbers[2]))

#lines
plt.plot(time, velocity, lw=0.8)

#labels
plt.xlabel('time [s]', size=25)
#plt.ylabel('velocity ' u"\u03C9" ' [rad/s]', size=25)
plt.ylabel('velocity [rad/s]', size=25)

#limits tuneados a mano
#  plt.xlim((0, 10))
plt.xticks(size=25)
#  plt.ylim((100, y))
plt.yticks(size=25)

plt.title('velocity vs. time curves', size=30)

velocity_mean=np.mean(velocity[-5:],axis=0)

#add line to file torques.txt
with open( "./curves/leftArm/joint" + jointName + "/torques" + jointName + ".txt", 'a') as f:
    f.write(str(velocity_mean) + " " + str(torque[0]) +"\n")

#show
plt.show()
