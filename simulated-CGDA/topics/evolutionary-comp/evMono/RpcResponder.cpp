// -*- mode:C++; tab-width:4; c-basic-offset:4; indent-tabs-mode:nil -*-

#include "RpcResponder.hpp"

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

    //pos->setPositionMode();
    //pos->positionMove(1, -35);

	StateP state (new State);

    // set the evaluation operator
    //state->setEvalOp(new FunctionMinEvalOp);
    FunctionMinEvalOp* functionMinEvalOp = new FunctionMinEvalOp; 
    functionMinEvalOp->setEffectsClient(effectsClient);
    functionMinEvalOp->setPRobot(probot);
    functionMinEvalOp->setPcamerasensordata(pcamerasensordata);
    functionMinEvalOp->setPlasersensordata(plasersensordata);
    functionMinEvalOp->setPsensorbaseC(psensorbaseC);
    functionMinEvalOp->setPsensorbaseL(psensorbaseL);
    functionMinEvalOp->setPimagen(pimagen);
    functionMinEvalOp->setPdepth(pdepth);
    functionMinEvalOp->setPenv(penv);
    functionMinEvalOp->setPcontrol(pcontrol);
    state->setEvalOp(functionMinEvalOp);

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

    out.clear();
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

void RpcResponder::setPcamerasensordata(const boost::shared_ptr<SensorBase::CameraSensorData>& _pcamerasensordata) {
    pcamerasensordata = _pcamerasensordata;
}

/************************************************************************/

void RpcResponder::setPlasersensordata(const boost::shared_ptr<SensorBase::LaserSensorData>& _plasersensordata) {
    plasersensordata = _plasersensordata;
}

/************************************************************************/
void RpcResponder::setPsensorbaseC(const SensorBasePtr& _psensorbaseC) {
    psensorbaseC = _psensorbaseC;
}

/************************************************************************/
void RpcResponder::setPsensorbaseL(const SensorBasePtr& _psensorbaseL) {
    psensorbaseL = _psensorbaseL;
}

/************************************************************************/
void RpcResponder::setPimagen(BufferedPort<yarp::sig::ImageOf<yarp::sig::PixelRgb> >* _pimagen) {
    pimagen = _pimagen;
}

/************************************************************************/
void RpcResponder::setPdepth(BufferedPort<yarp::sig::ImageOf<yarp::sig::PixelInt> >* _pdepth) {
    pdepth = _pdepth;
}

/************************************************************************/
void RpcResponder::setPenv(const EnvironmentBasePtr& _penv) {
    penv = _penv;
}

/************************************************************************/
void RpcResponder::setPcontrol(const ControllerBasePtr& _pcontrol) {
    pcontrol = _pcontrol;
}

/************************************************************************/

