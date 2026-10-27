# Continuous Goal-Directed Actions

## About

This code repository contains the algorithms developed for my PhD thesis. It also contains the research papers generated and the slides used for presenting the PhD and the research in conferences. The thesis was developed in the [Robotics Lab research group](http://roboticslab.uc3m.es) at [Universidad Carlos III de Madrid](http://www.uc3m.es).

The PhD defense video is available [online](http://www.dailymotion.com/video/x3w7qw0_defensa-tesis-doctoral-uc3m-santiago-morante_tech).

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

* [Robotics Lab profile](http://roboticslab.uc3m.es/roboticslab/people/s-morante)
* [Twitter](https://twitter.com/santimorante)
* [LinkedIn](https://es.linkedin.com/in/santimorante)
* [Dailymotion](http://www.dailymotion.com/santimorante)
* [Google Scholar](http://scholar.google.es/citations?user=7_fJykAAAAAJ&hl=en)
* [Coursera](https://www.coursera.org/user/i/86e993631015eb245c7401b6efee50b2)
* [Mendeley](https://www.mendeley.com/profiles/santiago-morante/)

