// -*- mode:C++; tab-width:4; c-basic-offset:4; indent-tabs-mode:nil -*-

#include "Babbling.hpp"

/************************************************************************/

void SetViewer(EnvironmentBasePtr penv, const string& viewername) {
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
    string viewername = "qtcoin";
    boost::thread thviewer(boost::bind(SetViewer,penv,viewername));
    string scenefilename = "../models/teo_cgda_iros.env.xml";
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

    KinBodyPtr objGreenPtr = penv->GetKinBody("objectGreen");
    if(!objGreenPtr) printf("[WorldRpcResponder] fail grab green object\n");
    else printf("[WorldRpcResponder] good grab green object\n");
    probot->Grab(objGreenPtr);


    // por lo visto no se agarra asi. habria que elegir link al que se engancha
    KinBodyPtr objRedPtr = penv->GetKinBody("objectRed");
    if(!objRedPtr) printf("[WorldRpcResponder] fail grab red object\n");
    else printf("[WorldRpcResponder] good grab red object\n");
    probot->Grab(objRedPtr);

    Transform T_base_green_object, T_base_red_object;
    double T_base_green_object_x, T_base_green_object_y,T_base_green_object_z;
    double T_base_red_object_x, T_base_red_object_y,T_base_red_object_z;

    while(1){

        std::vector<dReal> dEncRaw(probot->GetDOF());  // NUM_MOTORS
        dEncRaw[0+18] = rand() %100;  // simple
        dEncRaw[1+18] = rand() %100;  // simple
        dEncRaw[3+18] = rand() %100;  // simple
        dEncRaw[4+18] = rand() %100;


        //probot->SetJointValues(dEncRaw);
        pcontrol->SetDesired(dEncRaw); // This function "resets" physics
        while(!pcontrol->IsDone()) {
            boost::this_thread::sleep(boost::posix_time::milliseconds(1));
        }

        penv->StepSimulation(0.0001);  // StepSimulation must be given in seconds

        // Green object
        T_base_green_object = objGreenPtr->GetTransform();
        T_base_green_object_x = T_base_green_object.trans.x;
        T_base_green_object_y = T_base_green_object.trans.y;
        T_base_green_object_z = T_base_green_object.trans.z;

        // Red object
        T_base_red_object   = objRedPtr->GetTransform();
        T_base_red_object_x = T_base_red_object.trans.x;
        T_base_red_object_y = T_base_red_object.trans.y;
        T_base_red_object_z = T_base_red_object.trans.z;

        // cout << dEncRaw[0+18] << dEncRaw[1+18] << dEncRaw[2+18] << dEncRaw[3+18] << T_base_object_x << T_base_object_y << T_base_object_z;
    }
    return true;
}

/************************************************************************/

