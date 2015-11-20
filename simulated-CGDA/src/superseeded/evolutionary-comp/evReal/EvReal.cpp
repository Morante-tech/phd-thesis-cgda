// -*- mode:C++; tab-width:4; c-basic-offset:4; indent-tabs-mode:nil -*-

#include "EvReal.hpp"

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

bool EvReal::init() {
    if(! ::getenv("XGNITIVE_ROOT")) {
        printf("Required XGNITIVE_ROOT environomental variable empty!\n");
        printf("Include the line \"export XGNITIVE_ROOT=/your/path/to/xgnitive\" or similar in .profile or .bashrc\n");
        return false;
    }
    xgnitiveRoot = ::getenv("XGNITIVE_ROOT");

    bool ok = true;

    ok &= this->initOR();
    ok &= this->initSensor();

    return ok;
}

/************************************************************************/

bool EvReal::run() {

    while(1){
        boost::this_thread::sleep (boost::posix_time::seconds (5));
        cout << "EvReal alive..." << endl;
    }

    // target/goal configuration
    std::vector<dReal> activegoal;

    createConfPlan(activegoal);


    /*
    StateP state (new State);

    // set the evaluation operator
    FunctionMinEvalOp* functionMinEvalOp = new FunctionMinEvalOp;
    functionMinEvalOp->setPRobot(probot);
    functionMinEvalOp->setPenv(penv);
    functionMinEvalOp->setPcontrol(pcontrol);
    state->setEvalOp(functionMinEvalOp);

    //por aqui se muestran resultados
    printf("---------------------------> ");

    int newArgc = 2;
    char *newArgv[2] = { (char*)"unusedFirstParam", "../conf/evReal_ecf_params.xml" };

    state->initialize(newArgc, newArgv);
    state->run();

    vector<IndividualP> bestInd;
    FloatingPoint::FloatingPoint* genBest;
    vector<double> bestPoints;

    // final result
    bestInd = state->getHoF()->getBest();
    genBest = (FloatingPoint::FloatingPoint*) bestInd.at(0)->getGenotype().get();
    bestPoints = genBest->realValue;

    printf("-begin-\n");
    for(unsigned int i=0;i<bestPoints.size();i++)
        printf("%f, ",bestPoints[i]);
    printf("\n-end-\n");*/

    return true;
}

/************************************************************************/

bool EvReal::quit() {

    return true;
}

/************************************************************************/

bool EvReal::initOR() {

    RaveInitialize(true); // start openrave core
    penv = RaveCreateEnvironment(); // create the main environment
    RaveSetDebugLevel(Level_Debug);
    string viewername = "qtcoin";
    boost::thread thviewer(boost::bind(SetViewer,penv,viewername));
    string sceneFullName(xgnitiveRoot);  //-- used to use teo_cgda_iros.env.xml
    sceneFullName += "/main/app/default/models/openrave/teoFull.robot.xml";
    penv->Load(sceneFullName); // load the scene

    if(useMesh) {
        string meshFullName(xgnitiveRoot);
        meshFullName += "/main/app/default/models/openrave/objs/";
        meshFullName += meshName;
        meshFullName += ".obj";
        penv->Load(meshFullName); // load the mesh
        storeMeshKinBodyPtr = penv->GetKinBody(meshName);
        Transform t1(Vector(0.7071,0,0.7071,0),Vector(0,0,0.72));
        Transform t2(Vector(0.7071,0,0,-0.7071),Vector(0,0,0));
        storeMeshKinBodyPtr->SetTransform(t1*t2);
        /*std::vector<Transform> t1and2;
        t1and2.push_back( Transform (Vector(0.7071,0,0,-0.7071),Vector(0,0,0)) );
        t1and2.push_back( Transform(Vector(0.7071,0,0.7071,0),Vector(0,0,0.72)) );
        storeMeshKinBodyPtr->SetBodyTransformations(t1and2);*/
    }

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

    //KinBodyPtr objPtr = penv->GetKinBody("object");
    //if(!objPtr) printf("[WorldRpcResponder] fail grab\n");
    //else printf("[WorldRpcResponder] good grab\n");
    //probot->Grab(objPtr);

    return true;
}

/************************************************************************/

bool EvReal::initSensor() {

    //-- If using mesh, just return true acting like you did it.
    if(useMesh) return true;

    interface = new pcl::OpenNIGrabber();

    boost::function<void (const pcl::PointCloud<pcl::PointXYZ>::ConstPtr&)> f =
        boost::bind (&EvReal::sensorCallback, this, _1);

    interface->registerCallback (f);

    interface->start ();

    return true;
}

/************************************************************************/

bool EvReal::stopSensor() {
    //-- If using mesh, just return true acting like you did it.
    if(useMesh) return true;

    interface->stop ();
    return true;
}

/************************************************************************/

bool EvReal::quitSensor() {
    printf("bye!\n");

    //-- If using mesh, just return true acting like you did it.
    if(useMesh) return true;

    interface->stop ();
    delete interface;
    interface = 0;
    return true;
}


bool EvReal::createConfPlan(const std::vector<dReal> activegoal) {

    // what about http://openrave-users-list.185357.n3.nabble.com/How-to-use-real-sensor-data-for-planning-in-OpenRAVE-td4025956.html

    PlannerBase::PlannerParametersPtr params(new PlannerBase::PlannerParameters);
    params->SetRobotActiveJoints(probot); // sets the active joint indices
    probot->GetActiveDOFValues(params->vinitialconfig); // set initial config (use current robot configuration)
    params->vgoalconfig = activegoal;

    ///  Speed up (Optional): http://openrave.org/docs/0.6.6/coreapihtml/arch_planner.html
    ///  CollisionOptionsStateSaver optionstate(GetEnv()->GetCollisionChecker(),GetEnv()->GetCollisionChecker()->GetCollisionOptions()|CO_ActiveDOFs,false);

    // set other params values like

    PlannerBasePtr rrtplanner = RaveCreatePlanner(probot->GetEnv(),"rBiRRT");
    TrajectoryBasePtr ptraj = RaveCreateTrajectory(probot->GetEnv(),probot->GetActiveDOF());
    if( !rrtplanner->InitPlan(probot, params) ) {
        return false;
    }

    ///  Smooth Traj (Optional)
    /// _ProcessPostPlanners(RobotBasePtr probot, TrajectoryBasePtr ptraj);


    PlannerStatus status = rrtplanner->PlanPath(ptraj);
    if( status & PS_HasSolution ) {
        probot->SetActiveMotion(ptraj); // trajectory is done, execute on the robot
    }

}

/************************************************************************/

void EvReal::sensorCallback(const pcl::PointCloud<pcl::PointXYZ>::ConstPtr &cloud) {
    //cout << "Begin sensorCallback." << endl;
    gettimeofday(&start, NULL);

    //cout << "Begin removeNaNFromPointCloud, size: " << cloud->points.size() << "." << endl;
    std::vector<int> indices;
    pcl::PointCloud<pcl::PointXYZ>::Ptr modCloud1 (new pcl::PointCloud<pcl::PointXYZ>);
    //-- http://docs.pointclouds.org/1.7.0/group__filters.html#gac463283a9e9c18a66d3d29b28a575064
    //-- removeNaNFromPointCloud can be called with cloud_in == cloud_out
    //-- But can't here because we have a ConstPtr
    pcl::removeNaNFromPointCloud(*cloud, *modCloud1, indices);

    //cout << "Begin VoxelGrid, size: " << modCloud1->points.size() << "." << endl;
    //pcl::PointCloud<pcl::PointXYZ>::Ptr modCloud2 (new pcl::PointCloud<pcl::PointXYZ>);
    //pcl::VoxelGrid<pcl::PointXYZ> vg;
    //vg.setInputCloud (modCloud1);
    //vg.setLeafSize (0.005f, 0.005f, 0.005f);  // megmesh
    //vg.setLeafSize (0.01f, 0.01f, 0.01f);  // mesh
    //vg.setLeafSize (0.05f, 0.05f, 0.05f);  // boxes
    //vg.filter (*modCloud2);

    // \begin{raw point spheres}
    /*cout << "Begin operating with points, size: " << modCloud2->size() << "." << endl;
    std::vector<Vector> spheres(1);
    for(size_t point_index = 0; point_index < modCloud2->size(); point_index++) {
        spheres.push_back( Vector( modCloud2->points[point_index].x,
                                   modCloud2->points[point_index].y,
                                   modCloud2->points[point_index].z, 0.005 ));  // Last is radius.
    }
    { // lock the environment!
        OpenRAVE::EnvironmentMutex::scoped_lock lock(penv->GetMutex());
        KinBodyPtr ssphKinBodyPtr = RaveCreateKinBody(penv,"");
        ssphKinBodyPtr->SetName("ssphFromPCL");
        ssphKinBodyPtr->InitFromSpheres(spheres,true);
        //-- Remove previous
        if (storeSsphKinBodyPtr) penv->Remove(storeSsphKinBodyPtr);
        //-- Add new
        penv->Add(ssphKinBodyPtr,true);
        //-- Store for removal
        storeSsphKinBodyPtr = ssphKinBodyPtr;
    }  // the environment is not locked anymore*/
    // \end{raw point spheres}

    //cout << "Begin normal estimation + Poisson, size: " << modCloud2->points.size() << "." << endl;
    //-- thanks: http://www.pcl-users.org/Access-pcl-PolygonMesh-triangles-data-td4025718.html
    //pcl::NormalEstimation<pcl::PointXYZ, pcl::Normal> n;
    pcl::NormalEstimationOMP<pcl::PointXYZ, pcl::Normal> n;  //
    pcl::PointCloud<pcl::Normal>::Ptr normals (new pcl::PointCloud<pcl::Normal>);
    pcl::search::KdTree<pcl::PointXYZ>::Ptr tree (new pcl::search::KdTree<pcl::PointXYZ>);
    tree->setInputCloud(modCloud1);
    n.setInputCloud(modCloud1);
    n.setSearchMethod(tree);
    n.setKSearch (40);  // 20
    //n.setKSearch (modCloud2->size());
    //n.setNumberOfThreads(6);  // 1:7.8. 7:7.5. 20:7.4.
    n.compute (*normals);
    // Concatenate the XYZ and normal fields (cloud_with_normals = cloud + normals)
    pcl::PointCloud<pcl::PointNormal>::Ptr cloud_with_normals (new pcl::PointCloud<pcl::PointNormal>);
    pcl::concatenateFields (*modCloud1, *normals, *cloud_with_normals);
    // Create search tree
    pcl::search::KdTree<pcl::PointNormal>::Ptr tree2 (new pcl::search::KdTree<pcl::PointNormal>);
    tree2->setInputCloud (cloud_with_normals);
    pcl::Poisson<pcl::PointNormal> psr;  // Only pcl >= 1.6
    pcl::PolygonMesh triangles;
    psr.setInputCloud(cloud_with_normals);
    psr.setSearchMethod(tree2);
    psr.reconstruct(triangles);

    cout << "Begin operating with triangles, size: " << triangles.polygons.size() << "." << endl;
    pcl::PointCloud<pcl::PointXYZ> meshCloud;
    fromROSMsg (triangles.cloud, meshCloud);
    OpenRAVE::KinBody::Link::TRIMESH raveMesh;
    for(size_t triangle_index = 0; triangle_index < meshCloud.size(); triangle_index++) {
        // vert 0
        raveMesh.indices.push_back(3*triangle_index);
        size_t point0_index = triangles.polygons[triangle_index].vertices[0];
        raveMesh.vertices.push_back( Vector(meshCloud.points[point0_index].x,
                                            meshCloud.points[point0_index].y,
                                            meshCloud.points[point0_index].z) );
        // vert 1
        raveMesh.indices.push_back(1+3*triangle_index);
        size_t point1_index = triangles.polygons[triangle_index].vertices[1];
        raveMesh.vertices.push_back( Vector(meshCloud.points[point1_index].x,
                                            meshCloud.points[point1_index].y,
                                            meshCloud.points[point1_index].z) );
        // vert 2
        raveMesh.indices.push_back(2+3*triangle_index);
        size_t point2_index = triangles.polygons[triangle_index].vertices[2];
        raveMesh.vertices.push_back( Vector(meshCloud.points[point2_index].x,
                                            meshCloud.points[point2_index].y,
                                            meshCloud.points[point2_index].z) );
    }
    Transform t1(Vector(0.7071,0,0,-0.7071),Vector(0,0,0));
    raveMesh.ApplyTransform(t1);
    Transform t2(Vector(0.7071,0,0.7071,0),Vector(0,0,0.72));
    raveMesh.ApplyTransform(t2);

    { // lock the environment!
        OpenRAVE::EnvironmentMutex::scoped_lock lock(penv->GetMutex());
        KinBodyPtr meshKinBodyPtr = RaveCreateKinBody(penv,"");
        meshKinBodyPtr->SetName("m");
        meshKinBodyPtr->InitFromTrimesh(raveMesh,true);
        //-- Remove previous
        if (storeMeshKinBodyPtr) penv->Remove(storeMeshKinBodyPtr);
        //-- Add new
        penv->Add(meshKinBodyPtr,true);
        //-- Store for removal
        storeMeshKinBodyPtr=meshKinBodyPtr;
    }

    // \begin{raw point cubes}
    /*cout << "Begin operating with points, size: " << modCloud2->size() << "." << endl;
    std::vector<AABB> boxes(modCloud2->size());
    for(size_t point_index = 0; point_index < modCloud2->size(); point_index++) {
        boxes[point_index].extents = Vector(0.005,0.005,0.005);
        boxes[point_index].pos = Vector(modCloud2->points[point_index].x,
                                        modCloud2->points[point_index].y,
                                        modCloud2->points[point_index].z);
    }
    { // lock the environment!
        OpenRAVE::EnvironmentMutex::scoped_lock lock(penv->GetMutex());
        KinBodyPtr sboxKinBodyPtr = RaveCreateKinBody(penv,"");
        sboxKinBodyPtr->SetName("sboxFromPCL");
        sboxKinBodyPtr->InitFromBoxes(boxes,true);
        //-- Remove previous
        if (storeSboxKinBodyPtr) penv->Remove(storeSboxKinBodyPtr);
        //-- Add new
        penv->Add(sboxKinBodyPtr,true);
        //-- Store for removal
        storeSboxKinBodyPtr = sboxKinBodyPtr;
    }  // the environment is not locked anymore*/
    // \end{raw point cubes}

    //-- Output time
    gettimeofday(&end, NULL);
    seconds  = end.tv_sec  - start.tv_sec;
    useconds = end.tv_usec - start.tv_usec;
    mtime = ((seconds) * 1000 + useconds/1000.0) + 0.5;
    cout << "---------------------> Took: " << mtime << " milliseconds." << endl;
}

/************************************************************************/

bool EvReal::setMeshName(const char *meshName) {
    useMesh = true;
    this->meshName = meshName;
    return true;
}

/************************************************************************/
