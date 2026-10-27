# Friction and gravity compensation

Controllers that compensate the friction of the motors and gearboxes and the gravity of a robot
arm without force sensors, so that a person can guide the arm with little effort. Tested on one joint of the arm of the TEO humanoid robot.

Publications:

- S. Morante, J. G. Victores, S. Martínez and C. Balaguer, "Force-Sensorless Friction and Gravity
  Compensation for Robots", *ROBOT 2015: Second Iberian Robotics Conference*, Advances in
  Intelligent Systems and Computing, vol. 418, pp. 57-68.
  [doi:10.1007/978-3-319-27149-1_5](https://doi.org/10.1007/978-3-319-27149-1_5)
- S. Morante, J. G. Victores, S. Martínez and C. Balaguer, "Sensorless friction and gravity
  compensation", *Humanoids 2014*.
  [doi:10.1109/HUMANOIDS.2014.7041370](https://doi.org/10.1109/HUMANOIDS.2014.7041370)

## Contents

| Folder | Content |
|---|---|
| `testTorqueEncs/`, `testTorqueEncs2/` | C++ (YARP) programs that apply torques to a joint and record its encoders, and the recorded data (`torques/`) |
| `friction/` | Python scripts that analyse the recordings and fit the friction curves (`curves/`) |
| `frictionCompensator/` | C++ (YARP) compensator and recorded velocities |

## Status

The scripts in `friction/` run with Python 3 and the data in this folder.
`friction/vel_vs_time.py` appends its results to `curves/leftArm/joint22/torques22.txt`.
The C++ programs need YARP and the robot, and were not updated.
