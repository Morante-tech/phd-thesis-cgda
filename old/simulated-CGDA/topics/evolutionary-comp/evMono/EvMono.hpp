// -*- mode:C++; tab-width:4; c-basic-offset:4; indent-tabs-mode:nil -*-

#ifndef __EV_MONO_HPP__
#define __EV_MONO_HPP__

#include <yarp/os/all.h>

#include "RpcResponder.hpp"

#define DEFAULT_FILE_NAME "evMono_ecf_params.xml"

using namespace yarp::os;
using namespace yarp::dev;

class EvMono : public RFModule {
  private:
    RpcResponder rpcResponder;
    RpcServer rpcServer;
    Port effectsClient;
    RobotBasePtr probot;
    boost::shared_ptr<SensorBase::CameraSensorData> pcamerasensordata;
    boost::shared_ptr<SensorBase::LaserSensorData> plasersensordata;
    SensorBasePtr psensorbaseC;
    SensorBasePtr psensorbaseL;
    BufferedPort<yarp::sig::ImageOf<yarp::sig::PixelRgb> > p_imagen;
    BufferedPort<yarp::sig::ImageOf<yarp::sig::PixelInt> > p_depth;
    EnvironmentBasePtr penv;
    ControllerBasePtr pcontrol;

    bool interruptModule();
    double getPeriod();
    bool updateModule();

  public:
    bool configure(ResourceFinder &rf);
};

#endif  // __EV_MONO_HPP__

