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

    ///Openrave
    RaveInitialize(true); // start openrave core
    penv = RaveCreateEnvironment(); // create the main environment
    RaveSetDebugLevel(Level_Debug);
    string viewername = "qtcoin";
    boost::thread thviewer(boost::bind(SetViewer,penv,viewername));
    string scenefilename = "../3dmodel/env/teo_two_cylinders.env.xml";
    penv->Load(scenefilename); // load the scene
    //-- Get Robot 0
    std::vector<RobotBasePtr> robots;
    penv->GetRobots(robots);
    std::cout << "Robot 0: " << robots.at(0)->GetName() << std::endl;  // default: teo
    probot = robots.at(0);

    pcontrol = RaveCreateController(penv,"idealcontroller");
    /// Create the controllers, make sure to lock environment! (prevents changes)
    {
        EnvironmentMutex::scoped_lock lock(penv->GetMutex());
        std::vector<int> dofindices(probot->GetDOF());
        for(int i = 0; i < probot->GetDOF(); ++i) {
            dofindices[i] = i;
        }
        probot->SetController(pcontrol,dofindices,1); // control everything
    }


    ///Green Object
    KinBodyPtr objGreenPtr = penv->GetKinBody("objectGreen");
    if(!objGreenPtr) printf("[WorldRpcResponder] fail grab green object\n");
    else printf("[WorldRpcResponder] good grab green object\n");
    probot->Grab(objGreenPtr);

    // por lo visto no se agarra asi. habria que elegir link al que se engancha
    ///Red Object
    KinBodyPtr objRedPtr = penv->GetKinBody("objectRed");
    if(!objRedPtr) printf("[WorldRpcResponder] fail grab red object\n");
    else printf("[WorldRpcResponder] good grab red object\n");
    probot->Grab(objRedPtr);

    ///Declaring transformations
    Transform T_base_green_object, T_base_red_object;
    double T_base_green_object_x, T_base_green_object_y,T_base_green_object_z;
    double T_base_red_object_x, T_base_red_object_y,T_base_red_object_z;


    ///Opening CSV File

    time_t rawtime;
    struct tm * timeinfo;

    time ( &rawtime );
    timeinfo = localtime ( &rawtime );
    string filename("FeatureDataFile_");
    filename += asctime (timeinfo);
    filename += ".csv";

    ofstream dataFile;
    dataFile.open (filename.c_str());
    // joint 1 left, ... joint 4 left, joint 1 right, ..., joint 4 right, t_green_x, ..., t_red_x...
    dataFile << "IN,IN,IN,IN,IN,IN,IN,IN,OUT,OUT,OUT,OUT,OUT,OUT\n";

    for(int i=0; i<10000; i++){


        // cuidado con el orden de las joints al guardarlo en fichero, no confundas brazos!!
        // limites de ejes
        // que joints vamos a mover? cuales funcionan en teo?
        /// Right arm
        std::vector<dReal> dEncRaw(probot->GetDOF());  // NUM_MOTORS
        dEncRaw[0+18] = rand() %100;  // simple
        dEncRaw[1+18] = rand() %100;  // simple
        dEncRaw[3+18] = rand() %100;  // simple
        dEncRaw[4+18] = rand() %100;
        pcontrol->SetDesired(dEncRaw); // This function "resets" physics
        while(!pcontrol->IsDone()) {
            boost::this_thread::sleep(boost::posix_time::milliseconds(1));
        }

        // no se como se hace con el otro brazo
        /// Left arm
        std::vector<dReal> dEncRaw2(probot->GetDOF());  // NUM_MOTORS
        dEncRaw2[0+18] = rand() %100;  // simple
        dEncRaw2[1+18] = rand() %100;  // simple
        dEncRaw2[3+18] = rand() %100;  // simple
        dEncRaw2[4+18] = rand() %100;
        pcontrol->SetDesired(dEncRaw2); // This function "resets" physics
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


        // numero de encoder y orden de parametros por definir!!
        // cuando todo funcione, podemos/debemos meter variables compuestas x1-x2, etc
        dataFile << dEncRaw2[0+18] << "," << dEncRaw2[0+18] << "," << dEncRaw2[0+18] << "," << dEncRaw2[0+18] << ","
                 << dEncRaw2[0+18] << "," << dEncRaw2[0+18] << "," << dEncRaw2[0+18] << "," << dEncRaw2[0+18] << ","
                 << T_base_green_object_x << "," << T_base_green_object_y << "," << T_base_green_object_z << ","
                 << T_base_red_object_x << "," << T_base_red_object_y << "," << T_base_red_object_z << ","
                 <<  "\n";

    }


    dataFile.close();

    return true;
}

/************************************************************************/

