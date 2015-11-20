// -*- mode:C++; tab-width:4; c-basic-offset:4; indent-tabs-mode:nil -*-

#ifndef __RPC_RESPONDER_HPP__
#define __RPC_RESPONDER_HPP__

#include <ecf/ECF.h>
#include "FunctionMinEvalOp.hpp"

class RpcResponder  {
  protected:
    /**
    * Implement the actual responder (callback on RPC).
    */
    RobotBasePtr probot;
    EnvironmentBasePtr penv;
    ControllerBasePtr pcontrol;

};

#endif  // __RPC_RESPONDER_HPP__

