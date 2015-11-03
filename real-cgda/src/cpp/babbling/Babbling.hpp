// -*- mode:C++; tab-width:4; c-basic-offset:4; indent-tabs-mode:nil -*-


#ifndef __BABBLING_HPP__
#define __BABBLING_HPP__


#include <openrave-core.h>
#include <cstdlib>

using namespace OpenRAVE;
using namespace std;

class Babbling  {
  private:
    RobotBasePtr probot;
    EnvironmentBasePtr penv;
    ControllerBasePtr pcontrol;

  public:
    bool init();
};

#endif  // __BABBLING_HPP__

