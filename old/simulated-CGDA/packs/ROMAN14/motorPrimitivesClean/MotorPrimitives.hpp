// -*- mode:C++; tab-width:4; c-basic-offset:4; indent-tabs-mode:nil -*-

#ifndef __MOTOR_PRIMITIVES_HPP__
#define __MOTOR_PRIMITIVES_HPP__

#define __MOTOR_PRIMITIVES_HPP__

#include <iostream>  // cout


#include <openrave-core.h>  // openrave

#define DEBUG

//#define DEFAULT_ENV "../../../../contrib/pendant/evolutionary-comp/evMono6/models/teo_action_pretty.env.xml"
#define DEFAULT_ENV "../../../../contrib/pendant/evolutionary-comp/evMono6/models/teo_action_prettyT.env.xml"

//#define DEFAULT_CSV "/home/yo/svn/jgvictoresAsrob/xgnitive/packs/ROMAN14/db_500ms/db_xi50"
#define DEFAULT_CSV "../../db_var/db_full_33"

#define DEFAULT_USED_DOF 3

#define DEFAULT_MAX_DEPTH 2  // d in the paper
#define DEFAULT_EPSILON 20  // $\epsilon$ in the paper

using namespace OpenRAVE;
using namespace std;

class MotorPrimitives  {

    private:
        RobotBasePtr probot;
        EnvironmentBasePtr penv;
        ControllerBasePtr pcontrol;
        unsigned int totalDof;

        unsigned int usedDof;

        vector< vector < vector<dReal> > > primitiveCollection;  // vector<dReal> dEncRaw;

        double T_base_target_x;
        double T_base_target_y;
        double T_base_target_z;
        Transform T_base_kinect;
        Transform T_base_object;
        double targetX, targetY, targetZ;
        std::vector<KinBodyPtr> ssphKinBodyPtrs;
        KinBodyPtr objPtr;
        void targetDraw();
        void targetClean();

        double epsilon, maxDepth;

        void getCombinations(const int numElems, const int maxLevelDepth, vector< vector<int> >& res);
        void expandLevel(const int numElems, const int maxLevelDepth, const int level, vector<int>& levelVector, vector< vector<int> >& store);

        #ifdef DEBUG
            GraphHandlePtr pgraph;
            vector<RaveVector<float> > vpoints;
        #endif

    public:
        bool init();
        bool run();

        double compare(const vector<int>& sequence, vector<double>& how);
};

#endif  // __MOTOR_PRIMITIVES_HPP__

