# Evolutionary search of CGDA (superseded)

C++ programs that find, through evolutionary computation, the joint positions of the robot that
reproduce a generalized effect trajectory. The robot is simulated in OpenRAVE and the evolutionary
algorithm comes from [ECF](http://ecf.zemris.fer.hr/) (Evolutionary Computation Framework); its
parameters are in each `conf/*_ecf_params.xml`.

The folders are successive versions of the same program, kept as they were during the research:

| Folder | Notes |
|---|---|
| `monolithic/` | First version, everything in a single file (OpenRAVE + YARP) |
| `evMono/` ... `evMono4/`, `evMonoTest/` | Program split into `EvMono` (setup), `FunctionMinEvalOp` (fitness: how far the simulated effect is from the generalized one) and `RpcResponder` (YARP RPC interface) |
| `evMono5/` | Same structure, without the RPC responder implementation |
| `evMono6/`, `evMono6_IET/`, `evMono6_IETport/` | Latest simulated versions; `evMono6` and `evMono6_IET` no longer use YARP |
| `evReal/` | Later version (November 2015), with `EvReal` as entry point |

Each folder builds on its own with CMake. None of them was updated after 2016: they need
OpenRAVE, ECF and, for most versions, YARP.

Part of the PhD thesis of Santiago Morante (Robotics Lab, Universidad Carlos III de Madrid).
