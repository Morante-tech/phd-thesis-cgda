// -*- mode:C++; tab-width:4; c-basic-offset:4; indent-tabs-mode:nil -*-

#ifndef __CONNECTED_Matrices__
#define __CONNECTED_Matrices__

#include <yarp/os/RFModule.h>

#include <yarp/dev/all.h>

#include "ColorDebug.hpp"

#include "ProcessorPort.hpp"

namespace teo
{

/**
 * @ingroup ConnectedMatrices
 *
 * The ConnectedMatrices class implements a server part that receives a connection from a remote
 * \ref cartesianServer module.
 * 
 */
class ConnectedMatrices : public yarp::os::RFModule {

    public:

        ConnectedMatrices() {}
        bool configure(yarp::os::ResourceFinder &rf);

    protected:

        ProcessorPort inPort1;
        yarp::os::BufferedPort< yarp::sig::ImageOf< yarp::sig::PixelRgb > > inPort2;

        bool updateModule();
        bool interruptModule();
        // double getPeriod();

        yarp::os::BufferedPort< yarp::sig::ImageOf< yarp::sig::PixelMono > > outPort1;
        yarp::os::BufferedPort< yarp::sig::ImageOf< yarp::sig::PixelMono > > outPort2;
        yarp::os::BufferedPort< yarp::sig::ImageOf< yarp::sig::PixelMono > > outPort3;
        yarp::os::BufferedPort< yarp::sig::ImageOf< yarp::sig::PixelMono > > outPort4;
        yarp::os::BufferedPort< yarp::sig::ImageOf< yarp::sig::PixelMono > > outPort5;

};

}  // namespace teo

#endif  // __TEO_GRAVITY_COMPENSATOR__

