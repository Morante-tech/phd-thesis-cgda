// -*- mode:C++; tab-width:4; c-basic-offset:4; indent-tabs-mode:nil -*-

#include <stdio.h>
#include <stdlib.h>
#include <string>
#include <signal.h>
#include <yarp/os/all.h>
#include <yarp/dev/all.h>
#include <math.h>

using namespace yarp::os;
using namespace yarp::dev;

#define DEFAULT_AMPS 0
#define DEFAULT_FILE_NAME "empty.txt"

YARP_DECLARE_PLUGINS(ManipulationYarp);

static bool keepRunning = true;

void sigintHandler(int sig_num){
    keepRunning = false;
}

int main(int argc, char *argv[]) {

    double amps = DEFAULT_AMPS;
    std::string fileName = DEFAULT_FILE_NAME;

    YARP_REGISTER_PLUGINS(ManipulationYarp);

    ResourceFinder rf;
    rf.setVerbose(false);
    rf.setDefaultContext("testManipulationBot/conf");
    rf.setDefaultConfigFile("testManipulationBot.ini");
    rf.configure("MANIPULATION_ROOT", argc, argv);

    Property options;
    options.fromString(rf.toString());
    options.put("device","manipulationbot");  // because controlboard kills torque interface!
    PolyDriver dd(options);
    if(!dd.isValid()) {
      printf("RaveBot device not available.\n");
	  dd.close();
      Network::fini();
      return 1;
    }

    if (options.check("amps")) amps = options.find("amps").asDouble();
    if (options.check("file")) fileName = options.find("file").asString();
    printf("\t--amps (default: \"%f\")\n",amps);
    printf("\t--file (default: \"%s\")\n",fileName.c_str());

    FILE * pFile;
    int n;
    pFile = fopen (fileName.c_str(),"w");

    IPositionControl *pos;
    bool ok = dd.view(pos);
    if (!ok) {
        printf("[warning] Problems acquiring pos robot interface\n");
        return false;
    } else printf("[success] testTorque acquired pos robot interface\n");
	printf("Set position mode.\n");
    pos->setPositionMode();
    printf("test positionMove(0,30)\n");
    //pos->positionMove(0, -90);

    IEncoders *enc;
    ok = dd.view(enc);
    if (!ok) {
        printf("[warning] Problems acquiring enc robot interface\n");
        return false;
    } else printf("[success] testTorque acquired enc robot interface\n");

    ITorqueControl *trq;
    ok = dd.view(trq);
    if (!ok) {
        printf("[warning] Problems acquiring trq robot interface\n");
        return false;
    } else printf("[success] testTorque acquired trq robot interface\n");

    IControlMode *ctrl;
    ok = dd.view(ctrl);
    if (!ok) {
        printf("[warning] Problems acquiring ctrl robot interface\n");
        return false;
    } else printf("[success] testTorque acquired ctrl robot interface\n");

    printf("setTorqueMode in 1 seconds...\n");
    Time::delay(1);

    trq->setRefTorque(1,0);
    printf("setTorqueMode()\n");
    ctrl->setTorqueMode(1);

    printf("START LOOP\n");

    double time=0, timePrev=0, timeDiff=0, timeInitial=yarp::os::Time::now();
    double angle=0, anglePrev=0; 
    double velAng=0, velAngPrev=0, velAngAver=0;
    double motorConstant = 0.101;
    double kilos = 4.446;
    double newtons = kilos * 9.8;
    double metersCOG = 0.82 / 2.0;
    double newtonMeter=0;
    double cmdAmps=0;

    ::signal(SIGINT, sigintHandler);

    while(keepRunning) {

        Time::delay(20 / 1000.0);  // [s]
        //trq->getTorque(0,&t);
        enc->getEncoder(1,&angle);
        newtonMeter = newtons * metersCOG * sin(angle * M_PI/180.0);
        cmdAmps = amps + (newtonMeter / motorConstant) / 160.0;
        trq->setRefTorque(1,cmdAmps);

        time=yarp::os::Time::now();
        timeDiff=time - timePrev;

        velAng = (angle-anglePrev)/timeDiff;
        velAngAver = (velAng + velAngPrev) / 2.0;
        
        fprintf(pFile,"%f %f %f\n",amps,time-timeInitial,velAngAver);
        printf("------------> %f %f %f\n",cmdAmps,time-timeInitial,velAngAver);
        anglePrev=angle;
        timePrev=time;
        velAngPrev=velAng;
    }
    fclose(pFile);
    trq->setRefTorque(1,0);
    pos->setPositionMode();

    printf("----- Stopping Motor -----");

    return 1;
}


