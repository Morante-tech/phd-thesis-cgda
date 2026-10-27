"""
Plot the fitness of each individual of the evolutionary search (fitnessData.txt) and
mark the best one.

Part of the PhD thesis of Santiago Morante (Robotics Lab, Universidad Carlos III de Madrid).
"""


import numpy as np
import matplotlib.pyplot as plt

# example data
y = np.loadtxt("fitnessData.txt")
x = np.arange(len(y))

#lines
plt.plot(x, y, lw=0.4, label="fitness")

#minimum point
minarg= y.argmin()
plt.scatter(minarg,min(y), 75, color="red", label="Minimum point")

#labels
plt.xlabel('Individuals', size=30)
plt.ylabel('Log (Fitness)', size=30)

#limits tuneados a mano
plt.xlim((0, len(x)+10))
plt.xticks(size=25)

plt.ylim((100, max(y)))

plt.yticks(size=25)

plt.yscale('log')

plt.title('Fitness Evolution', size=30)
#plt.legend()
plt.show()
