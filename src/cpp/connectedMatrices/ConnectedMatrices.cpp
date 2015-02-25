// -*- mode:C++; tab-width:4; c-basic-offset:4; indent-tabs-mode:nil -*-

#include "ConnectedMatrices.hpp"

/************************************************************************/
bool teo::ConnectedMatrices::configure(yarp::os::ResourceFinder &rf) {

    //-- Open devices

    yarp::os::Property grabberOptions1;
    //-- Next lines for local cam1
    grabberOptions1.put("device","opencv_grabber");
    grabberOptions1.put("camera",1);
    grabberOptions1.put("framerate",15);
    //-- Next lines for remote cam1
    //grabberOptions1.put("device","remote_grabber"); // device type
    //grabberOptions1.put("local","/cm/1/img:i");     // name of local port to use
    //grabberOptions1.put("remote","/cm/1/img:o");    // name of remote port to connect to

    grabberDevice1.open(grabberOptions1);
    if (!grabberDevice1.isValid()) {
        CD_ERROR("!grabberDevice1.isValid()\n");
        return false;
    }

    yarp::os::Property grabberOptions2;
    //-- Next lines for local cam2
    grabberOptions2.put("device","opencv_grabber");
    grabberOptions2.put("camera",2);
    grabberOptions2.put("framerate",15);
    //-- Next lines for remote cam2
    //grabberOptions2.put("device","remote_grabber"); // device type
    //grabberOptions2.put("local","/cm/2/img:i");     // name of local port to use
    //grabberOptions2.put("remote","/cm/2/img:o");    // name of remote port to connect to
    grabberDevice2.open(grabberOptions2);
    if (!grabberDevice2.isValid()) {
        CD_ERROR("!grabberDevice2.isValid()\n");
        return false;
    }

    //-- View interfaces
    if ( ! grabberDevice1.view( processorRateThread.iFrameGrabberImage1 ) ) {
        CD_ERROR("Could not obtain iFrameGrabberImage1 interface.\n");
        return false;
    }
    if ( ! grabberDevice2.view( processorRateThread.iFrameGrabberImage2 ) ) {
        CD_ERROR("Could not obtain iFrameGrabberImage2 interface.\n");
        return false;
    }

    //-- Open out ports
    outPort1.open("/cm/1/out:i");
    outPort2.open("/cm/2/out:i");

    //-- Start the thread.
    return processorRateThread.start();
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

    processorRateThread.stop();

    grabberDevice1.close();
    grabberDevice2.close();

    return true;
}

/************************************************************************/

