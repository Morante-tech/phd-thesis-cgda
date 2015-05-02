
#ifndef FUNCTIONMINEVALOP_H_
#define FUNCTIONMINEVALOP_H_

#include <cmath>
#include <iostream>
#include <string>
#include <fstream>
#include <ecf/ECF.h>
#include <openrave-core.h>
#include <vector>
using namespace OpenRAVE;

#include <yarp/os/BufferedPort.h>
#include <yarp/os/Network.h>
#include <yarp/os/Port.h>
#include <yarp/os/RFModule.h>
#include <yarp/os/RateThread.h>

using namespace yarp::os;


class FunctionMinEvalOp : public EvaluateOp {

  public:
    void setPRobot(const RobotBasePtr& _probot) {
        probot = _probot;
    }
    void setPenv(const EnvironmentBasePtr& _penv){
        penv = _penv;
    }
    void setPcontrol(const ControllerBasePtr& _pcontrol){
        pcontrol = _pcontrol;
    }
    void setResults( vector<double>* _presults){
        pFresults = _presults;

    }

    void setIter(unsigned int* _piter){
        pIter = _piter;
    }

    void setPOutPort(Port* _pOutPort){
        pOutPort = _pOutPort;
    }

  public:
    FitnessP evaluate(IndividualP individual);
	void registerParameters(StateP);
	bool initialize(StateP);
    double getCustomFitness(vector<double> genPoints);
    RobotBasePtr probot;
    EnvironmentBasePtr penv;
    ControllerBasePtr pcontrol;
    KinBodyPtr _objPtr;
    KinBodyPtr _wall;
    vector<double>* pFresults;
    unsigned int* pIter;
    Transform T_base_object;

    Port* pOutPort;
};

typedef boost::shared_ptr<FunctionMinEvalOp> FunctionMinEvalOpP;

#endif /* FUNCTIONMINEVALOP_H_ */

