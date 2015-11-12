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
    string scenefilename = "../../../../3dmodel/env/teo_two_cylinders.env.xml";
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

    std::vector<RobotBase::ManipulatorPtr> vectorOfManipulatorPtr = probot->GetManipulators();
    for(size_t j=0;j<vectorOfManipulatorPtr.size();j++) {
        std::cout << "* Manipulator[" << j << "]: " << vectorOfManipulatorPtr[j]->GetName() << std::endl;
        std::vector< int > manipulatorIDs = vectorOfManipulatorPtr[j]->GetArmIndices();
        for(size_t k=0;k<manipulatorIDs.size();k++)
            std::cout << manipulatorIDs[k] << std::endl;
    }

    ///Green Object
    KinBodyPtr objGreenPtr = penv->GetKinBody("objectGreen");
    if(!objGreenPtr) printf("[WorldRpcResponder] fail grab green object\n");
    else printf("[WorldRpcResponder] good grab green object\n");
    probot->Grab(objGreenPtr,vectorOfManipulatorPtr[0]->GetEndEffector());  // 0 is rightArm

    ///Red Object
    KinBodyPtr objRedPtr = penv->GetKinBody("objectRed");
    if(!objRedPtr) printf("[WorldRpcResponder] fail grab red object\n");
    else printf("[WorldRpcResponder] good grab red object\n");
    probot->Grab(objRedPtr,vectorOfManipulatorPtr[1]->GetEndEffector());  // 1 is leftArm

    ///Declaring transformations
    Transform T_base_green_object, T_base_red_object;
    double T_base_green_object_x, T_base_green_object_y,T_base_green_object_z;
    double T_base_red_object_x, T_base_red_object_y,T_base_red_object_z;


    ///Opening CSV File

    time_t rawtime;
    struct tm * timeinfo;

    time ( &rawtime );
    timeinfo = localtime ( &rawtime );
    string filename("../../../../data/FeatureDataFile_");
    filename += asctime (timeinfo);
    filename += ".csv";

    ofstream dataFile;
    dataFile.open (filename.c_str());
    //  t_green_x, ..., t_red_x... joint 1 left, ... joint 4 left, joint 1 right, ..., joint 4 right,
    dataFile << "IN,IN_1,IN_2,IN_3,IN_4,IN_5,OUT,OUT_1,OUT_2,OUT_3,OUT_4,OUT_5,OUT_6,OUT_7,OUT_8,OUT_9,OUT_10,OUT_11\n";

    for(int i=0; i<1000; i++){

        // cuidado con el orden de las joints al guardarlo en fichero, no confundas brazos!!
        // limites de ejes estan raros, yo creo que mal
        std::vector<dReal> dEncRaw(probot->GetDOF());  // NUM_MOTORS
        /// Left arm
        dEncRaw[0+12] = -180 + float(((180 + 180) * rand()) / (RAND_MAX + 1.0));  // -180 180
        dEncRaw[1+12] = -10  + float(((100 + 10) * rand()) / (RAND_MAX + 1.0));  // -10 100
        dEncRaw[2+12] = -30  + float(((30  + 30) * rand()) / (RAND_MAX + 1.0));  // -30 30
        dEncRaw[3+12] = float(((135) * rand()) / (RAND_MAX + 1.0));  // 0 135
        dEncRaw[4+12] = -90 + float(((90 + 90) * rand()) / (RAND_MAX + 1.0));  // -90 90
        dEncRaw[5+12] = -90 + float(((90 + 90) * rand()) / (RAND_MAX + 1.0));  // -90 90
        /// Right arm
        dEncRaw[0+18] = -180 + float(((180 + 180) * rand()) / (RAND_MAX + 1.0));  // -180 180
        dEncRaw[1+18] = -10  + float(((100 + 10) * rand()) / (RAND_MAX + 1.0));  // -10 100
        dEncRaw[2+18] = -30  + float(((30  + 30) * rand()) / (RAND_MAX + 1.0));  // -30 30
        dEncRaw[3+18] = float(((135) * rand()) / (RAND_MAX + 1.0));  // 0 135
        dEncRaw[4+18] = -90 + float(((90 + 90) * rand()) / (RAND_MAX + 1.0));  // -90 90
        dEncRaw[5+18] = -90 + float(((90 + 90) * rand()) / (RAND_MAX + 1.0));  // -90 90
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

        // numero de encoder y orden de parametros por definir!!
        // cuando todo funcione, podemos/debemos meter variables compuestas x1-x2, etc
        dataFile << T_base_green_object_x << "," << T_base_green_object_y << "," << T_base_green_object_z << ","
                 << T_base_red_object_x << "," << T_base_red_object_y << "," << T_base_red_object_z << ","
                 << dEncRaw[0+12] << "," << dEncRaw[1+12] << "," << dEncRaw[2+12] << "," << dEncRaw[3+12] << ","
                 << dEncRaw[4+12] << "," << dEncRaw[5+12] << "," << dEncRaw[0+18] << "," << dEncRaw[1+18] << ","
                 << dEncRaw[2+18] << "," << dEncRaw[3+18] << "," << dEncRaw[4+18] << "," << dEncRaw[5+18] << ","
                 <<  "\n";

    }

    dataFile.close();

    return true;
}

/************************************************************************/

