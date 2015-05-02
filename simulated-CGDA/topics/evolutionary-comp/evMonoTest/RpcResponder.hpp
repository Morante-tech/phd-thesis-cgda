// -*- mode:C++; tab-width:4; c-basic-offset:4; indent-tabs-mode:nil -*-

#ifndef __RPC_RESPONDER_HPP__
#define __RPC_RESPONDER_HPP__

#include <yarp/os/all.h>
#include <yarp/dev/all.h>
#include <ecf/ECF.h>
#include "FunctionMinEvalOp.hpp"

#define VOCAB_DRAW VOCAB('d','r','a','w')
//#define VOCAB_FAILED VOCAB('f','a','i','l')
#define VOCAB_OK VOCAB2('o','k')
#define VOCAB_SET VOCAB3('s','e','t')
#define VOCAB_FIT VOCAB3('f','i','t')

using namespace yarp::os;
using namespace yarp::dev;

#define DEFAULT_HEIGHT 100
#define DEFAULT_WIDTH 100

class RpcResponder : public PortReader {
  protected:
    /**
    * Implement the actual responder (callback on RPC).
    */
    virtual bool read(ConnectionReader& connection);
    Port* effectsClient;
    RobotBasePtr probot;
    EnvironmentBasePtr penv;
    ControllerBasePtr pcontrol;

  public:
    void setEffectsClient(Port* _effectsClient);
    void setPRobot(const RobotBasePtr& _probot);
    void setPenv(const EnvironmentBasePtr& _penv);
    void setPcontrol(const ControllerBasePtr& _pcontrol);

};

#endif  // __RPC_RESPONDER_HPP__

