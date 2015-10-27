// -*- mode:C++; tab-width:4; c-basic-offset:4; indent-tabs-mode:nil -*-

#ifndef __MOTOR_PRIMITIVES_HPP__
#define __MOTOR_PRIMITIVES_HPP__

#define __MOTOR_PRIMITIVES_HPP__

#include <iostream>  // cout
#include <valarray>     // std::valarray
#include <stdlib.h>     // getenv

#include <openrave-core.h>  // openrave

#define DEBUG

#define DEFAULT_ENV "ris.env.xml"

#define DEFAULT_CSV "../../../ROMAN14/db_var/db_full_33"

#define DEFAULT_USED_DOF 3

#define DEFAULT_MAX_DEPTH 3  // d in the paper
#define DEFAULT_EPSILON 0.1  // $\epsilon$ in the paper

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

        KinBodyPtr objPtr;
        KinBodyPtr wallPtr;

        Transform T_base_object;
        int rows, cols;
        vector<int> sqAr;

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

        double compare(const vector<int>& sequence, const double& featureTarget);
};

#endif  // __MOTOR_PRIMITIVES_HPP__

