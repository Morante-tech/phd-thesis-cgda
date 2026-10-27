"""
Plot torque against velocity for joint 22 and fit one regression line for positive and
one for negative velocities (the friction model).

Part of the PhD thesis of Santiago Morante (Robotics Lab, Universidad Carlos III de Madrid).
"""

import os
import matplotlib.pyplot as plt
import numpy as np

# vectors data
velocity_plus = []
torque_plus = []
velocity_minus = []
torque_minus = []

velocity_zero=[]
torque_zero=[]

jointName="21"

# file
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "curves", "leftArm", "joint22", "torques22_noGrav_comp.txt"), 'r') as f:

#with open("./curves/leftArm/joint" + jointName + "/torques" + jointName + ".txt", 'r') as f:
    data = f.readlines()
    for line in data:
        numbers = line.split()
        if(float(numbers[0]) > 0.01):
            velocity_plus.append(float(numbers[0]))
            torque_plus.append(float(numbers[1]))

        elif(float(numbers[0]) < -0.01):
            velocity_minus.append(float(numbers[0]))
            torque_minus.append(float(numbers[1]))

        else:
            velocity_zero.append(float(numbers[0]))
            torque_zero.append(float(numbers[1]))

#lines
plt.scatter(velocity_plus, torque_plus, s=500, lw=1, color="red", edgecolor="black")
plt.scatter(velocity_minus, torque_minus, s=500, lw=1, color="green", edgecolor="black")
plt.scatter(velocity_zero, torque_zero, s=500, lw=1, color="blue", edgecolor="black")

#labels
plt.xlabel('velocity [degrees/s]', size=30)
plt.ylabel("I [A] " +  "\u03B1" + " torque [Nm]", size=30)

#regression (one for positive values, one for negative values)
regression_plus = np.polyfit(velocity_plus, torque_plus, 1)
regression_minus = np.polyfit(velocity_minus, torque_minus, 1)

#print "velocity > 0"
print("torque = " , regression_plus[0] , "*velocity + " , regression_plus[1] , "\n")

#print "velocity < 0"
print("torque = " , regression_minus[0] , "*velocity + " , regression_minus[1] , "\n")

# To visualize we need to generate actual values for the regression line.
r_x_p, r_y_p = list(zip(*((i, i*regression_plus[0] + regression_plus[1]) for i in range(60))))
plt.plot(r_x_p, r_y_p, lw=4, color="red")

r_x_m, r_y_m = list(zip(*((i, i*regression_minus[0] + regression_minus[1]) for i in range(-60,0))))
#plt.plot(np.array(r_x_m)-np.array(r_x_m)[-1], np.array(r_y_m)+2*np.array(r_y_m)[0], lw=4, color="green")
plt.plot(np.array(r_x_m), np.array(r_y_m), lw=4, color="green")

#plt.title('velocity vs. torque curves', size=30)
#plt.legend()

#limits tuneados a mano
#plt.xlim((-50, 50))
plt.xticks(size=25)
#plt.ylim((-1.5, 1.5))
plt.yticks(size=25)

plt.show()
