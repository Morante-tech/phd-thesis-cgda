
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

#include <openrave-core.h>


#define NUM_MOTORS    8.0

#define cameraWidth    64
#define cameraHeight   48

#define HEIGHT         512.0     // Base TransZ [mm]
#define PAN            0     // Base RotZ [deg]
#define TILT           -42.0     // Extra RotY [deg], neg looks down as in OpenNI, -42 goes good with real -50

using namespace yarp::os;
using namespace yarp::sig::draw;

using namespace OpenRAVE;

class FunctionMinEvalOp : public EvaluateOp {

  public:
    void setEffectsClient(Port* _effectsClient) {
        effectsClient = _effectsClient;
    }
    void setPRobot(const RobotBasePtr& _probot) {
        probot = _probot;
    }
    void setPenv(const EnvironmentBasePtr& _penv){
        penv = _penv;
    }
    void setPcontrol(const ControllerBasePtr& _pcontrol){
        pcontrol = _pcontrol;
    }
    void setX(double _targetX){
        targetX = _targetX;
    }
    void setY(double _targetY){
        targetY = _targetY;
    }
    void setZ(double _targetZ){
        targetZ = _targetZ;
    }

  public:
    FitnessP evaluate(IndividualP individual);
	void registerParameters(StateP);
	bool initialize(StateP);
    double getCustomFitness(vector<double> genPoints);
    Port *effectsClient;
    RobotBasePtr probot;
    EnvironmentBasePtr penv;
    ControllerBasePtr pcontrol;
    KinBodyPtr _objPtr;
    Transform T_base_kinect;
    Transform T_base_object;
    Transform T_kinect_object;
    double targetX, targetY, targetZ;

};

typedef boost::shared_ptr<FunctionMinEvalOp> FunctionMinEvalOpP;

#endif /* FUNCTIONMINEVALOP_H_ */

