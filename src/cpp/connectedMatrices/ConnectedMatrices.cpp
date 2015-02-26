// -*- mode:C++; tab-width:4; c-basic-offset:4; indent-tabs-mode:nil -*-

#include "ConnectedMatrices.hpp"

/************************************************************************/
bool teo::ConnectedMatrices::configure(yarp::os::ResourceFinder &rf) {

    //-- Open in ports
    inPort1.open("/1/img:i");
    inPort2.open("/2/img:i");

    //-- Open out ports
    outPort1.open("/adaptTypePredictor");
    outPort2.open("/frame1_reduced");
    outPort3.open("/frame2_reduced");
    outPort4.open("/adaptTypeWeight");
    outPort5.open("/error_image_2");
    inPort1.setPtrOutPort1( &outPort1 );
    inPort1.setPtrOutPort2( &outPort2 );
    inPort1.setPtrOutPort3( &outPort3 );
    inPort1.setPtrOutPort4( &outPort4 );
    inPort1.setPtrOutPort5( &outPort5 );

    //-- Start
    inPort1.start();

    return true;
}

/************************************************************************/
bool teo::ConnectedMatrices::updateModule() {
    CD_INFO("Alive\n");
    return true;
}

/************************************************************************/
bool teo::ConnectedMatrices::interruptModule() {

    outPort1.interrupt();
    outPort2.interrupt();
    outPort3.interrupt();
    outPort4.interrupt();
    outPort5.interrupt();

    inPort1.interrupt();
    inPort2.interrupt();

    inPort1.stop();

    return true;
}

/************************************************************************/

