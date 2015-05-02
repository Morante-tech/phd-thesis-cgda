
#ifndef FUNCTIONMINEVALOP_H_
#define FUNCTIONMINEVALOP_H_

#include <cmath>
#include <iostream>
#include <string>
#include <fstream>

//#include <yarp/math/Math.h>

#include <ecf/ECF.h>

#include <openrave-core.h>

using namespace OpenRAVE;

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
    void setX(double _targetX){
        targetX = _targetX;
    }
    void setY(double _targetY){
        targetY = _targetY;
    }
    void setZ(double _targetZ){
        targetZ = _targetZ;
    }

    void targetDraw(){
        T_base_target_x = T_base_kinect.trans.x*1000.0 - targetX;
        T_base_target_y = T_base_kinect.trans.y*1000.0 - targetY;
        T_base_target_z = T_base_kinect.trans.z*1000.0 - targetZ;
 
        printf("::: %.2f %.2f %.2f | %.2f %.2f %.2f\n",
                targetX, targetY, targetZ,
                T_base_target_x,T_base_target_x,T_base_target_z);
       
        { // lock the environment!           
        OpenRAVE::EnvironmentMutex::scoped_lock lock(penv->GetMutex());
        KinBodyPtr ssphKinBodyPtr = RaveCreateKinBody(penv,"");
        string ssphName("ssph_");
        std::ostringstream s;  // ssphName += std::to_string(ssphKinBodyPtrs.size()+1);  // C++11 only
        s << ssphKinBodyPtrs.size()+1;
        ssphName += s.str();
        ssphKinBodyPtr->SetName(ssphName.c_str());
        //
        std::vector<Vector> spheres(1);
        spheres.push_back( Vector(T_base_target_x/1000.0,T_base_target_y/1000.0,T_base_target_z/1000.0,0.010) );
        ssphKinBodyPtr->InitFromSpheres(spheres,true); 
        //
        penv->Add(ssphKinBodyPtr,true);
        ssphKinBodyPtrs.push_back(ssphKinBodyPtr);
        }  // the environment is not locked anymore
    }

    void targetClean(){
        for (unsigned int i=0;i<ssphKinBodyPtrs.size();i++)
            penv->Remove(ssphKinBodyPtrs[i]);
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
    Transform T_base_kinect;
    Transform T_base_object;
    //Transform T_kinect_object;
    double targetX, targetY, targetZ;
    std::vector<KinBodyPtr> ssphKinBodyPtrs;

    double T_base_target_x;
    double T_base_target_y;
    double T_base_target_z;

};

typedef boost::shared_ptr<FunctionMinEvalOp> FunctionMinEvalOpP;

#endif /* FUNCTIONMINEVALOP_H_ */

