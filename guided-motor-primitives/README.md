# Guided motor primitives

Execution of Continuous Goal-Directed Actions using motor primitives guided by the effects of
the action.

Publication: S. Morante, J. G. Victores, A. Jardón and C. Balaguer, "On using guided motor
primitives to execute Continuous Goal-Directed Actions", *RO-MAN 2014*, pp. 613-618.
[doi:10.1109/ROMAN.2014.6926320](https://doi.org/10.1109/ROMAN.2014.6926320)

## Contents

| Folder | Content |
|---|---|
| `db_1s/`, `db_500ms/`, `db_var/` | Recorded databases with different time steps (1 s, 500 ms and variable; `db_xi*` files) |
| `motorPrimitivesClean/`, `motorPrimitivesPaint/`, `src/motorPrimitivesGrab/` | C++ programs (YARP, OpenRAVE) that execute the primitives for each action |
| `src/roman14_*.py` | Plots of the paper |

## Status

`src/roman14_cleanPlot.py` and `src/roman14_paintPlot.py` run with Python 3.
`roman14_primitive.py` reads robot recordings that are not in this repository. The C++ code needs
YARP and OpenRAVE and was not updated.
