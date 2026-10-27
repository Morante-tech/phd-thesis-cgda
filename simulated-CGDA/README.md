# Simulated CGDA

Continuous Goal-Directed Actions in simulation: the robot generalizes the effects of several
demonstrations of an action, recognizes actions by comparing effects, and finds its own joint
movements that reproduce the effects through evolutionary computation.

Publications:

- S. Morante, J. G. Victores, A. Jardón and C. Balaguer, "Action effect generalization, recognition
  and execution through Continuous Goal-Directed Actions", *ICRA 2014*.
  [doi:10.1109/ICRA.2014.6907098](https://doi.org/10.1109/ICRA.2014.6907098)
- S. Morante, J. G. Victores, A. Jardón and C. Balaguer, "Humanoid robot imitation through
  continuous goal-directed actions: an evolutionary approach", *Advanced Robotics*, 2015.
  [doi:10.1080/01691864.2014.964314](https://doi.org/10.1080/01691864.2014.964314)

## Contents

| Folder | Content |
|---|---|
| `data/` | Generalized effects (`*Generalized`) and test queries (`*Query`) for five actions: fold, move, paint, rotate and wax, `normalized/` and `unnormalized/`. `waxEvolutionTraj2` is a trajectory obtained by the evolutionary search |
| `generalization/` | Generalization of several demonstrations into a single effect trajectory, using Gaussian Mixture Models and DBSCAN |
| `recognition/` | Action recognition by comparing effect trajectories with Dynamic Time Warping |
| `fitness/` | Plot of the fitness evolution of the evolutionary search |
| `results/` | Spreadsheet with the results |
| `src/` | `complete_real_old.py`, an early version that reads effects from a Kinect through YARP; `superseeded/` keeps the C++ evolutionary search (`evMono*`, `evReal`, built on ECF and OpenRAVE) and a YARP server that computes the effects |

## Status

`fitness/`, `recognition/` (except `recognition_test3.py`) and
`generalization/generalization_old_visual.py` run with Python 3 and the data in this folder.
The rest of `generalization/` reads demonstration recordings that were never stored in this
repository. The C++ code and `src/` need YARP, OpenRAVE and ECF and were not updated.
