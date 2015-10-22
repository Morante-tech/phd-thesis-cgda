// -*- mode:C++; tab-width:4; c-basic-offset:4; indent-tabs-mode:nil -*-

#include "EvMono.hpp"

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

bool EvMono::init() {

    RaveInitialize(true); // start openrave core
    penv = RaveCreateEnvironment(); // create the main environment
    RaveSetDebugLevel(Level_Debug);
    string viewername = "qtcoin";
    boost::thread thviewer(boost::bind(SetViewer,penv,viewername));
    string scenefilename = "../models/teo_action_pretty.env.xml";
    //string scenefilename = "/home/yo/teo/app/teoSim/models/teo_action_pretty.env.xml";
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


//double last = Time::now();
    //pos->setPositionMode();
    //pos->positionMove(1, -35);

    double target[3*POINTS] = {6.38762472700000e+02,2.72626977500000e+00,-3.97845084999999e+00,
                               6.42391811965000e+02,1.68573559950000e+01,-3.02628304000000e+00,
                               6.80641917184079e+02,8.88397871243782e+01,1.23043924875622e+00,
                               7.83047694335000e+02,1.20799710345000e+02,6.47513742499999e+00,
                               8.64809906691542e+02,5.41469797114429e+01,7.08611930348259e+00,
                               8.16733444044999e+02,-5.19248806450000e+01,-9.54816400000000e-01,
                               6.91319608447761e+02,-6.46731068507463e+01,-6.88174848258707e+00,
                               6.38455344905001e+02,-1.57018014900000e+01,-4.27471647499999e+00,
                               6.36920685935323e+02,3.73245194029851e-01,-3.83094820398010e+00};

	StateP state (new State);

    // set the evaluation operator
    //state->setEvalOp(new FunctionMinEvalOp);
    FunctionMinEvalOp* functionMinEvalOp = new FunctionMinEvalOp; 
    functionMinEvalOp->setPRobot(probot);
    functionMinEvalOp->setPenv(penv);
    functionMinEvalOp->setPcontrol(pcontrol);
        state->setEvalOp(functionMinEvalOp);

    vector< double > results;

    for(unsigned int i=0; i<POINTS; i++) {

        printf("---------------------------> i:%d\n",i);

        functionMinEvalOp->setX(target[0+i*3]);
        functionMinEvalOp->setY(target[1+i*3]);
        functionMinEvalOp->setZ(target[2+i*3]);

        int newArgc = 2;
        char *newArgv[2] = { (char*)"unusedFirstParam", "../conf/evMono_ecf_params.xml" };

        state->initialize(newArgc, newArgv);
        functionMinEvalOp->targetClean();
        functionMinEvalOp->targetDraw();

        state->run();

        vector<IndividualP> bestInd;
        FloatingPoint::FloatingPoint* genBest;
        vector<double> bestPoints;

        bestInd = state->getHoF()->getBest();
        genBest = (FloatingPoint::FloatingPoint*) bestInd.at(0)->getGenotype().get();
        bestPoints = genBest->realValue;

        results.push_back(bestPoints[0]);
        results.push_back(bestPoints[1]);
        results.push_back(bestPoints[2]);

    }

    printf("-begin-\n");
    for(unsigned int i=0;i<results.size();i++) printf("%f, ",results[i]);
    printf("\n-end-\n");

    return true;
}

/************************************************************************/

