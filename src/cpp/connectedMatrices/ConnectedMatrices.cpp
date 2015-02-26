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
    processorRateThread.setPtrOutPort1( &outPort1 );
    processorRateThread.setPtrOutPort2( &outPort2 );
    processorRateThread.setPtrOutPort3( &outPort3 );
    processorRateThread.setPtrOutPort4( &outPort4 );
    processorRateThread.setPtrOutPort5( &outPort5 );

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

    processorRateThread.stop();

    inPort1.close();
    inPort1.close();

    return true;
}

/************************************************************************/

