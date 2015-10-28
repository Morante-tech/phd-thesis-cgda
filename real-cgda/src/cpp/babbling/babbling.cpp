// -*- mode:C++; tab-width:4; c-basic-offset:4; indent-tabs-mode:nil -*-

#include "babbling.hpp"
/************************************************************************/

void SetViewer(EnvironmentBasePtr penv, const std::string& viewername) {
    ViewerBasePtr viewer = RaveCreateViewer(penv,viewername);
    BOOST_ASSERT(!!viewer);
    // attach it to the environment:
    penv->AttachViewer(viewer);
    // finally you call the viewer's infinite loop (this is why you need a separate thread):
    bool showgui = true;
    //   bool showgui = false;
    viewer->main(showgui);
}

/************************************************************************/

bool Babbling::init() {
    RaveInitialize(true); // start openrave core
    penv = RaveCreateEnvironment(); // create the main environment
    RaveSetDebugLevel(Level_Debug);
    std::string viewername = "qtcoin";
    boost::thread thviewer(boost::bind(SetViewer,penv,viewername));
    std::string scenefilename = "../../evMono6/models/teo_cgda_iros.env.xml";
    penv->Load(scenefilename); // load the scene
    //-- Get Robot 0
    std::vector<RobotBasePtr> robots;
    penv->GetRobots(robots);
    std::cout << "Robot 0: " << robots.at(0)->GetName() << std::endl;  // default: teo
    probot = robots.at(0);

    pcontrol = RaveCreateController(penv,"idealcontroller");
    // Create the controllers, make sure to lock environment! (prevents changes)
    {
        EnvironmentMutex::scoped_lock lock(penv->GetMutex());
        std::vector<int> dofindices(probot->GetDOF());
        for(int i = 0; i < probot->GetDOF(); ++i) {
            dofindices[i] = i;
        }
        probot->SetController(pcontrol,dofindices,1); // control everything
    }

    KinBodyPtr objPtr = penv->GetKinBody("object");
    if(!objPtr) printf("[WorldRpcResponder] fail grab\n");
    else printf("[WorldRpcResponder] good grab\n");
    probot->Grab(objPtr);

    /* initialize random seed: */
    srand (time(NULL));
    // while mucho

    for(int t=0;t<10000;t++) {
        std::vector<dReal> dEncRaw(probot->GetDOF());  // NUM_MOTORS
        dEncRaw[0+18] = std::rand() % 100;  // simple
        dEncRaw[1+18] = std::rand()% 100;  // simple
        dEncRaw[3+18] = std::rand()% 100;  // simple
        dEncRaw[4+18] = std::rand()% 100;

        std::cout << std::endl << " joints: "<< dEncRaw[0+18] << ","<< dEncRaw[1+18] << ","<< dEncRaw[2+18] << ","<< dEncRaw[3+18] << "\n";

        probot->SetJointValues(dEncRaw);
        pcontrol->SetDesired(dEncRaw); // This function "resets" physics
        while(!pcontrol->IsDone()) {
            boost::this_thread::sleep(boost::posix_time::milliseconds(1));
        }

        // obetener de redObjPtr y greenObjPtr centroide

        //cout << std::endl << " feature: "<< ...

        penv->StepSimulation(0.0001);  // StepSimulation must be given in seconds
    }
    return true;
}

/************************************************************************/

