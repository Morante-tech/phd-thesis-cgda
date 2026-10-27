# Continuous Goal-Directed Actions

Code and data of my PhD thesis, *"Continuous Goal-Directed Actions: Advances in Robot Learning"*,
defended in March 2016 at the [Robotics Lab](https://roboticslab.uc3m.es) of
[Universidad Carlos III de Madrid](https://www.uc3m.es), supervised by Juan G. Victores and
Carlos Balaguer.

The thesis proposes a robot imitation paradigm in which the robot learns the **effects** that
an action produces on the environment (how the features of the objects change) instead of
copying the movements of the demonstrator. The robot then searches for its own movements that
reproduce those effects.

> **Research archive.** This repository is kept for reference and is no longer developed.
> The thesis, the defense slides and the conference slides are attached to the
> [v1.0-tesis release](https://github.com/Morante-tech/phd-thesis-cgda/releases/tag/v1.0-tesis).
> The defense video is on [Dailymotion](http://www.dailymotion.com/video/x3w7qw0_defensa-tesis-doctoral-uc3m-santiago-morante_tech).

## Contents and publications

| Folder | Content | Publication |
|---|---|---|
| [`simulated-CGDA/`](simulated-CGDA) | CGDA in simulation: generalization of action effects, recognition with DTW, and execution through evolutionary computation | ICRA 2014 ([doi:10.1109/ICRA.2014.6907098](https://doi.org/10.1109/ICRA.2014.6907098)); Advanced Robotics 2015 ([doi:10.1080/01691864.2014.964314](https://doi.org/10.1080/01691864.2014.964314)) |
| [`guided-motor-primitives/`](guided-motor-primitives) | Execution of CGDA by combining motor primitives guided by the effects | RO-MAN 2014 ([doi:10.1109/ROMAN.2014.6926320](https://doi.org/10.1109/ROMAN.2014.6926320)) |
| [`friction-gravity-compensation/`](friction-gravity-compensation) | Friction and gravity compensation without force sensors, on an arm of the TEO humanoid robot | ROBOT 2015 ([doi:10.1007/978-3-319-27149-1_5](https://doi.org/10.1007/978-3-319-27149-1_5)); Humanoids 2014 ([doi:10.1109/HUMANOIDS.2014.7041370](https://doi.org/10.1109/HUMANOIDS.2014.7041370)) |
| [`demonstration-feature-selection/`](demonstration-feature-selection) | Automatic selection of good demonstrations and relevant features (Dissimilarity Mapping Filtering) | Humanoids 2015 ([doi:10.1109/HUMANOIDS.2015.7363569](https://doi.org/10.1109/HUMANOIDS.2015.7363569)) |
| [`real-cgda/`](real-cgda) | CGDA with the TEO robot: motor babbling and a neural network that maps object features to joint or Cartesian positions | PhD thesis |
| [`object-object-centered-actions/`](object-object-centered-actions) | Pointer to the master's thesis work on object-object centered actions | Master's thesis (in the release) |
| [`abandoned/`](abandoned) | A line of research that was abandoned: connecting movements between images | - |

## Python scripts

The Python scripts were ported from Python 2 to Python 3 in 2026. `mlpy` and the old
`dtw` library no longer exist, so Dynamic Time Warping now comes from
[dissimilarity-mapping-filtering](https://github.com/Morante-tech/dissimilarity-mapping-filtering).
The C++ code (YARP, OpenRAVE) was not updated and documents how the experiments were run.

```bash
pip install -r requirements.txt
./run_python_scripts.sh   # runs every script whose data is in this repository
```

| Status | Scripts |
|---|---|
| Run with the data in this repository (checked by CI) | `demonstration-feature-selection/`, `friction-gravity-compensation/friction/`, `guided-motor-primitives/src/roman14_cleanPlot.py` and `roman14_paintPlot.py`, `simulated-CGDA/fitness/`, `simulated-CGDA/recognition/` (except `recognition_test3.py`), `simulated-CGDA/generalization/generalization_old_visual.py` |
| Need recordings that were never in this repository | the rest of `simulated-CGDA/generalization/`, `simulated-CGDA/recognition/recognition_test3.py`, `guided-motor-primitives/src/roman14_primitive.py`, `abandoned/` (videos removed from the history) |
| Need the robot middleware YARP | `simulated-CGDA/src/` |
| Need the FANN C library (`fann2`) | `real-cgda/src/python/`, `abandoned/connected-images/src/python/main_nn.py` |

`friction-gravity-compensation/friction/vel_vs_time.py` also runs, but appends its results to
`curves/leftArm/joint22/torques22.txt`.

## Related repositories and removed files

* The demonstration and feature selection algorithm (`demonstration-feature-selection/`) is also maintained as a standalone project in [dissimilarity-mapping-filtering](https://github.com/Morante-tech/dissimilarity-mapping-filtering).
* The thesis, the defense slides, the master's thesis and the conference slides are attached to the [v1.0-tesis release](https://github.com/Morante-tech/phd-thesis-cgda/releases/tag/v1.0-tesis).
* The 3D models of the TEO humanoid robot used by `real-cgda/` were removed from this repository; they are published by the Robotics Lab in [teo-openrave-models](https://github.com/roboticslab-uc3m/teo-openrave-models).
* Raw videos and trained network weights were removed from the history to keep the repository small.

## License

Unless otherwise noted, all the code contained in this repository is open-source and licensed under the [MIT License](LICENSE).

## Links

* [Google Scholar](http://scholar.google.es/citations?user=7_fJykAAAAAJ&hl=en)
* [LinkedIn](https://es.linkedin.com/in/santimorante)
* [Dailymotion](http://www.dailymotion.com/santimorante)
* [Coursera](https://www.coursera.org/user/i/86e993631015eb245c7401b6efee50b2)
