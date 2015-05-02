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
    string scenefilename = "../models/teo_action.env.xml";
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

    //-- Get Robot 1's camera ptr, description and name
    std::vector<RobotBase::AttachedSensorPtr> sensors;
    sensors = robots.at(1)->GetAttachedSensors();

    psensorbaseL = sensors.at(0)->GetSensor();
    if(psensorbaseL == NULL) printf("[error] Bad sensorbaseL, may break in future because of this.\n");
    else printf("Good sensorbase...\n");
    std::string tipo = psensorbaseL->GetDescription();
    printf("%s\n",tipo.c_str());
    tipo = psensorbaseL->GetName();
    printf("%s\n",tipo.c_str());
    if (psensorbaseL->Supports(SensorBase::ST_Laser)) printf("[monolithic] success: Sensor 0 supports ST_Laser.\n");
    psensorbaseL->Configure(SensorBase::CC_PowerOn);
    psensorbaseL->Configure(SensorBase::CC_RenderDataOn);
    plasersensordata = boost::dynamic_pointer_cast<SensorBase::LaserSensorData>(psensorbaseL->CreateSensorData(SensorBase::ST_Laser));

    psensorbaseC = sensors.at(1)->GetSensor();
    if(psensorbaseC == NULL) printf("[error] Bad sensorbaseC, may break in future because of this.\n");
    else printf("Good sensorbase...\n");
    std::string tipo2 = psensorbaseC->GetDescription();
    printf("%s\n",tipo2.c_str());
    tipo = psensorbaseC->GetName();
    printf("%s\n",tipo2.c_str());
    if (psensorbaseC->Supports(SensorBase::ST_Camera)) printf("[monolithic] success: Sensor 1 supports ST_Camera.\n");
    psensorbaseC->Configure(SensorBase::CC_PowerOn);
    boost::shared_ptr<SensorBase::CameraGeomData> pcamerageomdata = boost::dynamic_pointer_cast<SensorBase::CameraGeomData>(psensorbaseC->GetSensorGeometry(SensorBase::ST_Camera));
    int camWidth = pcamerageomdata->width;
    int camHeight = pcamerageomdata->height;
    printf("Camera width: %d, height: %d.\n",camWidth,camHeight);
    pcamerasensordata = boost::dynamic_pointer_cast<SensorBase::CameraSensorData>(psensorbaseC->CreateSensorData(SensorBase::ST_Camera));

    psensorbaseC->SimulationStep(0.1);
    while( ! (pcamerasensordata->vimagedata.size() > 0 ) ) {
        psensorbaseC->GetSensorData(pcamerasensordata);
        printf("wait cam\n");
        Time::delay(.5);
    }

    p_imagen.open("/evMono/rgb:o");
    p_depth.open("/evMono/depth:o");

    effectsClient.open("/evMono/effects:o");

    rpcResponder.setEffectsClient(&effectsClient);
    rpcResponder.setPimagen(&p_imagen);
    rpcResponder.setPdepth(&p_depth);
    rpcResponder.setPRobot(probot);
    rpcResponder.setPcamerasensordata(pcamerasensordata);
    rpcResponder.setPlasersensordata(plasersensordata);
    rpcResponder.setPsensorbaseC(psensorbaseC);
    rpcResponder.setPsensorbaseL(psensorbaseL);
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
    p_imagen.interrupt();
    p_depth.interrupt();
    effectsClient.close();
    rpcServer.close();
    p_imagen.close();
    p_depth.close();
    return true;
}

/************************************************************************/

