// -*- mode:C++; tab-width:4; c-basic-offset:4; indent-tabs-mode:nil -*-

/*
 * Guided motor primitives for the clean action (RO-MAN 2014): searches the combination of
 * primitives, up to a maximum depth, whose effect is closest to the generalized trajectory.
 *
 * Part of the PhD thesis of Santiago Morante (Robotics Lab, Universidad Carlos III de Madrid).
 * Not updated since 2016: needs OpenRAVE.
 */

#include "MotorPrimitives.hpp"

/************************************************************************/

bool MotorPrimitives::run() {

    #ifdef DEBUG
        std::cout << "[info] \\begin{run()}" << std::endl;
        for(int i=6;i>0;i--){
            std::cout << "[info] Start in " << i << "..." << std::endl;
            usleep(1.0*pow(10,6));
        }
    #endif  // DEBUG

    const size_t targetSize = 9;
    // target is X in the paper, the feature trajectory.
    double target[targetSize*3] = {6.38762472700000e+02,2.72626977500000e+00,-3.97845084999999e+00,
                                 6.42391811965000e+02,1.68573559950000e+01,-3.02628304000000e+00,
                                 6.80641917184079e+02,8.88397871243782e+01,1.23043924875622e+00,
                                 7.83047694335000e+02,1.20799710345000e+02,6.47513742499999e+00,
                                 8.64809906691542e+02,5.41469797114429e+01,7.08611930348259e+00,
                                 8.16733444044999e+02,-5.19248806450000e+01,-9.54816400000000e-01,
                                 6.91319608447761e+02,-6.46731068507463e+01,-6.88174848258707e+00,
                                 6.38455344905001e+02,-1.57018014900000e+01,-4.27471647499999e+00,
                                 6.36920685935323e+02,3.73245194029851e-01,-3.83094820398010e+00};

    // sequenceUsed is P in the paper, the sequence of primitives used.
    vector<int> sequenceUsed;  // Start out empty.

    // For all targets
    for(int targetIdx=0; targetIdx<targetSize; targetIdx++) {  // target loop
        
        targetX = target[3*targetIdx];
        targetY = target[1+3*targetIdx];
        targetZ = target[2+3*targetIdx];

        #ifdef DEBUG
            //targetClean();
            //j//targetDraw();
        #endif  // DEBUG    

        bool targetFound = false;

        vector<int> lowestCostPath;
        double costOfLowestCostPath = std::numeric_limits<double>::max();

        ///
        {
            //int x[] = {8,23,23,0,4,7,10,3,4,11,3,20,10,10,13,2,8,7,8,8,1,21};
            int x[] = {0,14,25,32,13,13,12,13,30,18,13,17,7,31,32,10,5,32,7,2,18,13,13,10,27};
            std::vector<int> sequenceToCompare(x, x + sizeof x / sizeof x[0]);
            vector<double> where(3);
            double cost = compare(sequenceToCompare, where);
            int a;
            std::cin >> a;
        }   
        ///

        int depth = 1;
        vector<double> lowWhere(3);
        while ((depth<=maxDepth) && (!targetFound)) {  // depth loop
            #ifdef DEBUG
                std::cout << "[info] Attempting for depth: " << depth << std::endl;
            #endif  // DEBUG    
            vector< vector<int> > combinations;
            getCombinations(primitiveCollection.size(), depth, combinations);

            unsigned int sequenceIdx = 0;
            while ((sequenceIdx<combinations.size()) && (!targetFound)) {  // search the combinations within the same depth loop
                #ifdef DEBUG
                    std::cout << "Compare sequence " << sequenceIdx << ": ";
                    for(unsigned int inner=0;inner<combinations[sequenceIdx].size();inner++) {
                        std::cout << combinations[sequenceIdx][inner] << " " ;
                    }
                    std::cout << std::endl;
                #endif  // DEBUG
                //j// double cost = compare(combinations[sequenceIdx], target[targetIdx]);  // gone because we must pre-append (next 5 lines of code/comments)
                // begin: must pre-append sequenceUsed (learned from previous targets)
                vector<int> sequenceToCompare = sequenceUsed;  // should deep copy: http://www.cplusplus.com/reference/vector/vector/operator=/
                // sequenceToCompare.append(combinations[sequenceIdx]);  // thanks: http://stackoverflow.com/questions/2551775/c-appending-a-vector-to-a-vector
                sequenceToCompare.insert( sequenceToCompare.end(), combinations[sequenceIdx].begin(), combinations[sequenceIdx].end() );
                // end: must pre-append sequenceUsed (learned from previous targets)
                vector<double> where(3);
                double cost = compare(sequenceToCompare, where);
                #ifdef DEBUG
                    std::cout << "Cost: " << cost << std::endl;
                #endif  // DEBUG
                if (cost < epsilon) {
                    // sequenceUsed.append(combinations[sequenceIdx]);  // thanks: http://stackoverflow.com/questions/2551775/c-appending-a-vector-to-a-vector
                    sequenceUsed.insert(sequenceUsed.end(), combinations[sequenceIdx].begin(), combinations[sequenceIdx].end() );
                    targetFound = true;
                    //#ifdef DEBUG
                        std::cout << "[success] ********** targetIdx[" << targetIdx << "] achieved!!! Reached [" << where[0] << "," << where[1] << "," << where[2] << "]. Cost: " << cost <<" **********" << std::endl;
                    //#endif  // DEBUG
                } else {
                    if (cost < costOfLowestCostPath) {
                        lowestCostPath = combinations[sequenceIdx];
                        costOfLowestCostPath = cost;
                        lowWhere[0] = where[0];
                        lowWhere[1] = where[1];
                        lowWhere[2] = where[2];
                    }
                }
                sequenceIdx++;
            }  // while ((sequenceIdx<combinations.size()) && (!targetFound)  // search the combinations within the same depth loop
            depth++;
        }  // while ((depth<=maxDepth) && (!targetFound))  // depth loop
        if(!targetFound) { 
            //#ifdef DEBUG
                std::cout << "[warning] ******* targetIdx[" << targetIdx << "] not found within defined maxDepth. Reached ["  << lowWhere[0] << "," << lowWhere[1] << "," << lowWhere[2] << "]. Appending costOfLowestCostPath=" << costOfLowestCostPath << " ******* " << std::endl;
            //#endif  // DEBUG
            sequenceUsed.insert(sequenceUsed.end(), lowestCostPath.begin(), lowestCostPath.end() );
        }
    }  // for(int targetIdx=0; targetIdx<targetSize; targetIdx++)  // target loop
 
    //#ifdef DEBUG
        std::cout << "Full sequence used: ";
        for(unsigned int inner=0;inner<sequenceUsed.size();inner++) {
            std::cout << sequenceUsed[inner] << " " ;
        }
        std::cout << std::endl;
    //#endif  // DEBUG
   
    #ifdef DEBUG
        std::cout << "[info] \\end{run()}" << std::endl;
    #endif  // DEBUG

    return true;
}

/************************************************************************/

void MotorPrimitives::getCombinations(const int numElems, const int maxLevelDepth, vector< vector<int> >& res) {
    vector<int> levelVector;
    expandLevel(numElems, maxLevelDepth, 0, levelVector, res);
}

/************************************************************************/

void MotorPrimitives::expandLevel(const int numElems, const int maxLevelDepth, const int level, vector<int>& levelVector, vector< vector<int> >& store) {
    for (int i=0;i<numElems;i++) {
        vector<int> levelVectorCopy = levelVector;
        levelVectorCopy.push_back(i);
        if(level+1 < maxLevelDepth) {  // level+1 to avoid previous 2 steps of future level
            expandLevel(numElems, maxLevelDepth, level+1, levelVectorCopy, store);
        } else {
            store.push_back(levelVectorCopy);
        }
    }
}

/************************************************************************/

void SetViewer(EnvironmentBasePtr penv, const string& viewername) {
    ViewerBasePtr viewer = RaveCreateViewer(penv,viewername);
    BOOST_ASSERT(!!viewer);
    // attach it to the environment:
    penv->AttachViewer(viewer);
    // finally you call the viewer's infinite loop (this is why you need a separate thread):
    #ifdef DEBUG
        bool showgui = true;
    #else
        bool showgui = false;
    #endif  // DEBUG
    viewer->main(showgui);
}

/************************************************************************/

bool MotorPrimitives::init() {

    epsilon = DEFAULT_EPSILON;
    maxDepth = DEFAULT_MAX_DEPTH;

    usedDof = DEFAULT_USED_DOF;

    RaveInitialize(true); // start openrave core
    penv = RaveCreateEnvironment(); // create the main environment
    RaveSetDebugLevel(Level_Debug);
    boost::thread thviewer(boost::bind(SetViewer,penv,"qtcoin"));
    string scenefilename = DEFAULT_ENV;
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
        totalDof = probot->GetDOF();
        std::vector<int> dofindices(totalDof);
        for(unsigned int i = 0; i < totalDof; ++i) {
            dofindices[i] = i;
        }
        probot->SetController(pcontrol,dofindices,1); // control everything
    }

    objPtr = penv->GetKinBody("object");
    if (!objPtr) {
        std::cerr << "[warning] object \"object\" does not exist." << std::endl;
    } else {
        #ifdef DEBUG
            std::cout << "[sucess] object \"object\" exists." << std::endl;
        #endif  // DEBUG
    }
    probot->Grab(objPtr);

    T_base_object = objPtr->GetTransform();
    printf("object \"object\" at %f %f %f.\n", T_base_object.trans.x, T_base_object.trans.y, T_base_object.trans.z);

    KinBodyPtr kinectPtr = penv->GetKinBody("kinect");
    if(!kinectPtr) {
        std::cerr << "[warning] object \"kinect\" does not exist." << std::endl;
    } else printf("sucess: object \"kinect\" exists.\n");
    T_base_kinect = kinectPtr->GetTransform();
    printf("object \"kinect\" at %f %f %f.\n", T_base_kinect.trans.x, T_base_kinect.trans.y, T_base_kinect.trans.z);

    usleep(1*pow(10,6));

    std::ifstream ifs(DEFAULT_CSV);
    if(!ifs.is_open()) {
        std::cerr << "[error] Bad file open." << std::endl;
        return -1;
    }
    string line;
    while (getline(ifs, line)) {
        vector< vector<double> > store;
        int beginPos=0;
        int endPos=0;
        while ((beginPos = (int)line.find('[', endPos)) != string::npos) {
            endPos = (int)line.find(']', beginPos);
            string subs = line.substr(beginPos+1, endPos-beginPos-1);
            beginPos = endPos;
            double id, timestamp, q1, q2, q3;
            std::sscanf(subs.c_str(), "%lf, %lf, %lf, %lf, %lf", &id, &timestamp, &q1, &q2, &q3);
            vector<double> trio(3);
            trio[0] = q1;
            trio[1] = q2;
            trio[2] = q3;
            store.push_back(trio);
        }
        primitiveCollection.push_back(store);
    }   
    ifs.close();

    #ifdef DEBUG
        for(int outest=0;outest<primitiveCollection.size();outest++) {
            std::cout << "---action: " << outest << std::endl;
            for(int outer=0;outer<primitiveCollection[outest].size();outer++) {
                std::cout << outer << ": ";
                for(int inner=0;inner<primitiveCollection[outest][outer].size();inner++) {
                    std::cout << primitiveCollection[outest][outer][inner] << " " ;
                }
                std::cout << std::endl;
            }
        }
    #endif  // DEBUG

    return true;
}

/************************************************************************/

double MotorPrimitives::compare(const vector<int>& sequence, vector<double>& how) {

    vector<dReal> rawPoss(totalDof, 0.0);  // Start primitive from zero
    rawPoss[18+0] = -15.0 * M_PI/180.0;  // Primitive in rad, pass to rad for openrave.
    rawPoss[18+3] = -15.0 * M_PI/180.0;  // Primitive in rad, pass to rad for openrave.

    for(unsigned int primitiveIdx=0; primitiveIdx<sequence.size(); primitiveIdx++) {  // Perform the primitive.
        #ifdef DEBUG
            std::cout << "[info] * Perform sequence[primitiveIdx]: " << sequence[primitiveIdx] << std::endl;
        #endif  // DEBUG
        for(unsigned int stepIdx=0; stepIdx < primitiveCollection[sequence[primitiveIdx]].size(); stepIdx++) {  // Pêrform each step of the primitive.
            #ifdef DEBUG
                //std::cout << "[info] ** Perform stepIdx: " << stepIdx << std::endl;
            #endif  // DEBUG
            // primitiveCollection[primitiveIdx][stepIdx] is a vector<dReal>  // Add primitives sequentially
            rawPoss[18+0] += -1.0 * primitiveCollection[sequence[primitiveIdx]][stepIdx][0] * M_PI/180.0;  // Primitive in rad, pass to rad for openrave.
            rawPoss[18+1] += -1.0 * primitiveCollection[sequence[primitiveIdx]][stepIdx][1] * M_PI/180.0;  // Primitive in rad, pass to rad for openrave.
            rawPoss[18+3] += -1.0 * primitiveCollection[sequence[primitiveIdx]][stepIdx][2] * M_PI/180.0;  // Primitive in rad, pass to rad for openrave.
            probot->SetJointValues(rawPoss);
            //pcontrol->SetDesired(rawPoss); // This function "resets" physics ??
            //while(!pcontrol->IsDone()) {
            //    boost::this_thread::sleep(boost::posix_time::milliseconds(1));
            //}
            //penv->StepSimulation(0.0001);  // StepSimulation must be given in seconds

            #ifdef DEBUG
                // draw the end effector of the trajectory
                vpoints.push_back(objPtr->GetTransform().trans);
                const float lineThickness = 4.0f;
                // const float lineColors[3] = {0,1,0};  // gominola
                const RaveVector< float > lineColors = RaveVector< float >(0, 0, 1, 1);
                pgraph = penv->drawlinestrip(&vpoints[0].x,vpoints.size(),sizeof(vpoints[0]),lineThickness,lineColors);
            #endif  // DEBUG
        }

        #ifdef DEBUG
            //usleep(0.2*pow(10,6));
        #endif  // DEBUG

    }

    T_base_object = objPtr->GetTransform();

    double T_base_object_x = T_base_object.trans.x*1000.0;  // Pass to mm.
    double T_base_object_y = T_base_object.trans.y*1000.0;  // Pass to mm.
    double T_base_object_z = T_base_object.trans.z*1000.0;  // Pass to mm.

    how[0] = T_base_kinect.trans.x*1000.0 - T_base_object_x;
    how[1] = T_base_kinect.trans.y*1000.0 - T_base_object_y;
    how[2] = T_base_kinect.trans.z*1000.0 - T_base_object_z;

    T_base_target_x = T_base_kinect.trans.x*1000.0 - targetX;
    T_base_target_y = T_base_kinect.trans.y*1000.0 - targetY;
    T_base_target_z = T_base_kinect.trans.z*1000.0 - targetZ;

    double cost = sqrt ( pow(T_base_object_x-T_base_target_x,2) + pow(T_base_object_y-T_base_target_y,2) + pow(T_base_object_z-T_base_target_z,2) );
    #ifdef DEBUG
        std::cout << "[info] * at: " << T_base_object_x << ", "<< T_base_object_y << ", "<< T_base_object_z << "." << std::endl;
        std::cout << "[info] * compare w.r.t. " << T_base_target_x << ", "<< T_base_target_y << ", "<< T_base_target_z << "." << std::endl;
        std::cout << "[info] * cost (return value): " << cost <<  std::endl;
        vpoints.clear();
    #endif  // DEBUG
    return cost;
}

/************************************************************************/

void MotorPrimitives::targetDraw() {
    T_base_target_x = T_base_kinect.trans.x*1000.0 - targetX;
    T_base_target_y = T_base_kinect.trans.y*1000.0 - targetY;
    T_base_target_z = T_base_kinect.trans.z*1000.0 - targetZ;
 
    printf("::: %.2f %.2f %.2f | %.2f %.2f %.2f\n",
            targetX, targetY, targetZ,
            T_base_target_x,T_base_target_x,T_base_target_z);
       
    { // lock the environment!           
        OpenRAVE::EnvironmentMutex::scoped_lock lock(penv->GetMutex());
        KinBodyPtr ssphKinBodyPtr = RaveCreateKinBody(penv,"");
        string ssphName("ssph_");
        std::ostringstream s;  // ssphName += std::to_string(ssphKinBodyPtrs.size()+1);  // C++11 only
        s << ssphKinBodyPtrs.size()+1;
        ssphName += s.str();
        ssphKinBodyPtr->SetName(ssphName.c_str());
        //
        std::vector<Vector> spheres(1);
        spheres.push_back( Vector(T_base_target_x/1000.0,T_base_target_y/1000.0,T_base_target_z/1000.0,0.010) ); 
        ssphKinBodyPtr->InitFromSpheres(spheres,true); 
        //
        penv->Add(ssphKinBodyPtr,true);
        ssphKinBodyPtrs.push_back(ssphKinBodyPtr);
    }  // the environment is not locked anymore
}

/************************************************************************/

void MotorPrimitives::targetClean(){
    for (unsigned int i=0;i<ssphKinBodyPtrs.size();i++)
        penv->Remove(ssphKinBodyPtrs[i]);
}

/************************************************************************/

