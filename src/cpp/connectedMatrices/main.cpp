// -*- mode:C++; tab-width:4; c-basic-offset:4; indent-tabs-mode:nil -*-

#include "ColorDebug.hpp"
#include "ConnectedMatrices.hpp"

int main(int argc, char *argv[]) {

    yarp::os::ResourceFinder rf;
    rf.setVerbose(true);
    rf.setDefaultContext("connectedMatrices");
    rf.setDefaultConfigFile("connectedMatrices.ini");
    rf.configure(argc,argv);

    teo::ConnectedMatrices mod;
    if(rf.check("help")) {
        return mod.runModule(rf);
    }

    CD_INFO("Run \"connectedMatrices --help\" for options.\n");
    CD_INFO("connectedMatrices checking for yarp network...\n");
    yarp::os::Network yarp;
    if (!yarp.checkNetwork()) {
        CD_ERROR("Found no yarp network (try running \"yarpserver &\"), bye!\n");
        return -1;
    }
    CD_SUCCESS("Found Yarp network.\n");

    return mod.runModule(rf);
}

