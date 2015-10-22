// -*- mode:C++; tab-width:4; c-basic-offset:4; indent-tabs-mode:nil -*-

#include "RpcResponder.hpp"

#define POINTS 9

/*************************************************************************/

bool RpcResponder::read(ConnectionReader& connection) {

    Bottle cmd, out;
    cmd.read(connection);
    printf("[RpcResponder] Got %s\n", cmd.toString().c_str());
    out.clear();
    ConnectionWriter *returnToSender = connection.getWriter();
    if (returnToSender==NULL) return false;
    if(cmd.get(0).asString() != "start") {
        printf("[fail] unknown command, only \"start\" for now.\n");
        out.clear();
        out.addVocab(VOCAB_FAILED);
        out.write(*returnToSender);  // send reply.
        return true;
    }
    double last = Time::now();
    //pos->setPositionMode();
    //pos->positionMove(1, -35);

    double target[3*POINTS] = {6.38762472700000e+02,2.72626977500000e+00,-3.97845084999999e+00,
                               6.42391811965000e+02,1.68573559950000e+01,-3.02628304000000e+00,
                               6.80641917184079e+02,8.88397871243782e+01,1.23043924875622e+00,
                               7.83047694335000e+02,1.20799710345000e+02,6.47513742499999e+00,
                               8.64809906691542e+02,5.41469797114429e+01,7.08611930348259e+00,
                               8.16733444044999e+02,-5.19248806450000e+01,-9.54816400000000e-01,
                               6.91319608447761e+02,-6.46731068507463e+01,-6.88174848258707e+00,
                               6.38455344905001e+02,-1.57018014900000e+01,-4.27471647499999e+00,
                               6.36920685935323e+02,3.73245194029851e-01,-3.83094820398010e+00};

	StateP state (new State);

    // set the evaluation operator
    //state->setEvalOp(new FunctionMinEvalOp);
    FunctionMinEvalOp* functionMinEvalOp = new FunctionMinEvalOp; 
    functionMinEvalOp->setEffectsClient(effectsClient);
    functionMinEvalOp->setPRobot(probot);
    functionMinEvalOp->setPenv(penv);
    functionMinEvalOp->setPcontrol(pcontrol);
        state->setEvalOp(functionMinEvalOp);

    out.clear();

    for(int i = 0; i<POINTS; i++) {

        functionMinEvalOp->setX(target[0+i*3]);
        functionMinEvalOp->setY(target[1+i*3]);
        functionMinEvalOp->setZ(target[2+i*3]);



        int newArgc = 2;
        char *newArgv[2] = { (char*)"unusedFirstParam", "../conf/evMono_ecf_params.xml" };

        printf("[RpcResponder] ---------------------------1\n");

        state->initialize(newArgc, newArgv);

        printf("[RpcResponder] ---------------------------1\n");

        state->run();

        printf("[RpcResponder] --------------------------2\n");

        vector<IndividualP> bestInd;
        FloatingPoint::FloatingPoint* genBest;
        vector<double> bestPoints;

        bestInd = state->getHoF()->getBest();
        genBest = (FloatingPoint::FloatingPoint*) bestInd.at(0)->getGenotype().get();
        bestPoints = genBest->realValue;

        out.addDouble(bestPoints[0]);
        out.addDouble(bestPoints[1]);
        out.addDouble(bestPoints[2]);

        printf("%d: Done in %f s.\n",i,Time::now()-last);
    }

    out.addVocab(VOCAB_OK);
    out.write(*returnToSender);  // send reply.

    return true;
}

/************************************************************************/

void RpcResponder::setEffectsClient(Port* _effectsClient) {
    effectsClient = _effectsClient;
}

/************************************************************************/

void RpcResponder::setPRobot(const RobotBasePtr& _probot) {
    probot = _probot;
}

/************************************************************************/

/************************************************************************/
void RpcResponder::setPenv(const EnvironmentBasePtr& _penv) {
    penv = _penv;
}

/************************************************************************/
void RpcResponder::setPcontrol(const ControllerBasePtr& _pcontrol) {
    pcontrol = _pcontrol;
}

/************************************************************************/

