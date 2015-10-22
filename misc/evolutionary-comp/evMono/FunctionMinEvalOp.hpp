
#ifndef FUNCTIONMINEVALOP_H_
#define FUNCTIONMINEVALOP_H_

#include <cmath>
#include <iostream>
#include <string>
#include <fstream>
#include <yarp/os/all.h>
#include <yarp/sig/all.h>

#include <yarp/math/Math.h>

#include <ecf/ECF.h>

#include "cv.h"

#include "TravisLib.hpp"
#include "TinyMath.hpp"

#include <openrave-core.h>


#define NUM_MOTORS    8.0

#define cameraWidth    128
#define cameraHeight    96

#define FX_D          64.0
#define FY_D          48.0
#define CX_D          64.0
#define CY_D          48.0
#define FX_RGB        64.0
#define FY_RGB        48.0
#define CX_RGB        64.0
#define CY_RGB        48.0

#define HEIGHT         512.0     // Base TransZ [mm]
#define PAN            0     // Base RotZ [deg]
#define TILT           -42.0     // Extra RotY [deg], neg looks down as in OpenNI, -42 goes good with real -50

using namespace yarp::os;
using namespace yarp::sig::draw;

using namespace cv;

using namespace OpenRAVE;

class FunctionMinEvalOp : public EvaluateOp {

  public:
    void setEffectsClient(Port* _effectsClient) {
        effectsClient = _effectsClient;
    }
    void setPRobot(const RobotBasePtr& _probot) {
        probot = _probot;
    }
    void setPcamerasensordata(const boost::shared_ptr<SensorBase::CameraSensorData>& _pcamerasensordata){
        pcamerasensordata = _pcamerasensordata;
    }
    void setPlasersensordata(const boost::shared_ptr<SensorBase::LaserSensorData>& _plasersensordata){
        plasersensordata = _plasersensordata;
    }
    void setPsensorbaseC(const SensorBasePtr& _psensorbaseC){
        psensorbaseC = _psensorbaseC;
    }
    void setPsensorbaseL(const SensorBasePtr& _psensorbaseL){
        psensorbaseL = _psensorbaseL;
    }
    void setPimagen(BufferedPort<yarp::sig::ImageOf<yarp::sig::PixelRgb> >* _pimagen){
        p_imagen = _pimagen;
    }
    void setPdepth(BufferedPort<yarp::sig::ImageOf<yarp::sig::PixelInt> >* _pdepth){
        p_depth = _pdepth;
    }
    void setPenv(const EnvironmentBasePtr& _penv){
        penv = _penv;
    }
    void setPcontrol(const ControllerBasePtr& _pcontrol){
        pcontrol = _pcontrol;
    }

  public:
    FitnessP evaluate(IndividualP individual);
	void registerParameters(StateP);
	bool initialize(StateP);
    double getCustomFitness(vector<double> genPoints);
    Port *effectsClient;
    RobotBasePtr probot;
    boost::shared_ptr<SensorBase::CameraSensorData> pcamerasensordata;
    boost::shared_ptr<SensorBase::LaserSensorData> plasersensordata;
    SensorBasePtr psensorbaseC;
    SensorBasePtr psensorbaseL;
    EnvironmentBasePtr penv;
    ControllerBasePtr pcontrol;
    BufferedPort<yarp::sig::ImageOf<yarp::sig::PixelRgb> >* p_imagen;
    BufferedPort<yarp::sig::ImageOf<yarp::sig::PixelInt> >* p_depth;

};

typedef boost::shared_ptr<FunctionMinEvalOp> FunctionMinEvalOpP;

#endif /* FUNCTIONMINEVALOP_H_ */

