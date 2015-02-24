// -*- mode:C++; tab-width:4; c-basic-offset:4; indent-tabs-mode:nil -*-

#ifndef __CONNECTED_Matrices__
#define __CONNECTED_Matrices__

#include <yarp/os/RFModule.h>

#include <yarp/dev/all.h>

#include "ColorDebug.hpp"

#include "ProcessorRateThread.hpp"

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

        ProcessorRateThread processorRateThread;

        yarp::dev::PolyDriver grabberDevice1;
        yarp::dev::PolyDriver grabberDevice2;

        bool updateModule();
        bool interruptModule();
        // double getPeriod();

        yarp::os::BufferedPort< yarp::sig::ImageOf< yarp::sig::PixelBgr > > outPort1;
        yarp::os::BufferedPort< yarp::sig::ImageOf< yarp::sig::PixelBgr > > outPort2;

};

}  // namespace teo

#endif  // __TEO_GRAVITY_COMPENSATOR__

