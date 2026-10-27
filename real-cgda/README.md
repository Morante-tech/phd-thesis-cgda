# Real CGDA

Continuous Goal-Directed Actions with the TEO humanoid robot: motor babbling to explore which
effects the robot can produce, and a neural network that learns an inverse model from object
features to joint or Cartesian positions. This work is part of the PhD thesis.

## Contents

| Folder | Content |
|---|---|
| `src/cpp/babbling/` | C++ motor babbling in OpenRAVE |
| `src/python/` | Training of the inverse model with FANN neural networks (`main_offline.py`) |
| `data/` | Recorded object features (`FeatureDataFile_*.csv`) |
| `3dmodel/` | OpenRAVE scene and robot description (XML). The 3D meshes of TEO were removed from this repository; they are published in [teo-openrave-models](https://github.com/roboticslab-uc3m/teo-openrave-models) |

## Status

`src/python/main_offline.py` was ported to Python 3 but needs the FANN C library
(`pip install fann2` after installing libfann). The C++ code needs OpenRAVE and was not updated.
