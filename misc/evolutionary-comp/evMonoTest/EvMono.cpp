// -*- mode:C++; tab-width:4; c-basic-offset:4; indent-tabs-mode:nil -*-

#include "EvMono.hpp"

void SetViewer(EnvironmentBasePtr penv, const string& viewername)
{
    ViewerBasePtr viewer = RaveCreateViewer(penv,viewername);
    BOOST_ASSERT(!!viewer);

    // attach it to the environment:
    penv->AttachViewer(viewer);

    // finally you call the viewer's infinite loop (this is why you need a separate thread):
    //bool showgui = true;
    bool showgui = false;
    viewer->main(showgui);
    
}

/************************************************************************/

bool EvMono::configure(ResourceFinder &rf) {

    RaveInitialize(true); // start openrave core
    penv = RaveCreateEnvironment(); // create the main environment
    RaveSetDebugLevel(Level_Debug);
    string viewername = "qtcoin";
    boost::thread thviewer(boost::bind(SetViewer,penv,viewername));
    //string scenefilename = "../models/teo_action.env.xml";
    string scenefilename = "/home/yo/teo/app/teoSim/models/teo_action_pretty.env.xml";
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
//        printf("HERE: %d\n",i);
      }
      probot->SetController(pcontrol,dofindices,1); // control everything
    }

    KinBodyPtr objPtr = penv->GetKinBody("object");
    if(!objPtr) printf("[WorldRpcResponder] fail grab\n");
    else printf("[WorldRpcResponder] good grab\n");
    probot->Grab(objPtr);

    effectsClient.open("/evMono/effects:o");

    rpcResponder.setEffectsClient(&effectsClient);
    rpcResponder.setPRobot(probot);
    rpcResponder.setPenv(penv);
    rpcResponder.setPcontrol(pcontrol);
    rpcServer.setReader(rpcResponder);
    rpcServer.open("/evMono/rpc:i");

    return true;
}

/************************************************************************/
double EvMono::getPeriod() {
    return 5.0;  // Fixed, in seconds, the slow thread that calls updateModule below
}

/************************************************************************/
bool EvMono::updateModule() {
    //printf("EvMono alive...\n");
    return true;
}

/************************************************************************/

bool EvMono::interruptModule() {
    printf("EvMono closing...\n");
    effectsClient.interrupt();
    rpcServer.interrupt();
    effectsClient.close();
    rpcServer.close();
    return true;
}

/************************************************************************/

