// -*- mode:C++; tab-width:4; c-basic-offset:4; indent-tabs-mode:nil -*-

#include <openrave-core.h>
#include <cmath>
#include <iostream>
#include <string>
#include <fstream>
#include <openrave-core.h>
#include <vector>
#include <cstdlib>

#ifndef __BABBLING_HPP__
#define __BABBLING_HPP__
using namespace OpenRAVE;


class Babbling  {
  private:
    RobotBasePtr probot;
    EnvironmentBasePtr penv;
    ControllerBasePtr pcontrol;
  public:
    KinBodyPtr _redObjPtr;
    KinBodyPtr _greenObjPtr;

    bool init();
};

#endif  // __BABBLING_HPP__

