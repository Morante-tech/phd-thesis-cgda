// -*- mode:C++; tab-width:4; c-basic-offset:4; indent-tabs-mode:nil -*-

/*
 * Guided motor primitives for the paint action (RO-MAN 2014): searches the combination of
 * primitives, up to a maximum depth, whose effect (percentage of painted wall) is closest
 * to the generalized one.
 *
 * Part of the PhD thesis of Santiago Morante (Robotics Lab, Universidad Carlos III de Madrid).
 * Not updated since 2016: needs OpenRAVE.
 */

#include "MotorPrimitives.hpp"

/************************************************************************/

bool MotorPrimitives::run() {  // init() was called before.

    #ifdef DEBUG  // This miniblock is just a countdown to start because of the viewer.
        std::cout << "[info] \\begin{run()}" << std::endl;
        for(int i=5;i>0;i--) {
            std::cout << "[info] Start in " << i << "..." << std::endl;
            usleep(1.0*pow(10,6));
        }
    #endif  // DEBUG

    const size_t targetSize = 17;
    // target is X in the paper, the feature trajectory.
    double target[targetSize]={0, 6.25, 12.5, 18.75, 25, 31.25, 37.5
                   , 43.75, 50, 56.25, 62.5, 68.75, 75, 81.25, 87.5, 93.75, 100};

    // sequenceUsed is P in the paper, the sequence of primitives used.
    vector<int> sequenceUsed;  // Start out empty.

    // For all targets
    for(int targetIdx=0; targetIdx<targetSize; targetIdx++) {  // target loop

        bool targetFound = false;

        vector<int> lowestCostPath;
        double costOfLowestCostPath = std::numeric_limits<double>::max();

        ///
        {
            //int x[] = {10,28,28,0,1,5,21,4,4,13,5,2,4,2,2,8,17,10,10,1,11,19};
            int x[] = {0,14,25,32,13,13,12,13,30,18,13,17,7,31,32,10,5,32,7,2,18,13,13,10,27};
            std::vector<int> sequenceToCompare(x, x + sizeof x / sizeof x[0]);
            double where;
            double cost = compare(sequenceToCompare, where);
            int a;
            std::cin >> a;
        }   
        ///

        int depth = 1;
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
                double cost = compare(sequenceToCompare, target[targetIdx]);
                #ifdef DEBUG
                    std::cout << "Cost: " << cost << std::endl;
                #endif  // DEBUG
                if (cost < epsilon) {
                    // sequenceUsed.append(combinations[sequenceIdx]);  // thanks: http://stackoverflow.com/questions/2551775/c-appending-a-vector-to-a-vector
                    sequenceUsed.insert(sequenceUsed.end(), combinations[sequenceIdx].begin(), combinations[sequenceIdx].end() );
                    targetFound = true;
                    //#ifdef DEBUG
                        std::cout << "[success] ********** targetIdx[" << targetIdx << "]=" << target[targetIdx] << " achieved!!! **********" << std::endl;
                    //#endif  // DEBUG
                } else {
                    if (cost < costOfLowestCostPath) {
                        lowestCostPath = combinations[sequenceIdx];
                        costOfLowestCostPath = cost;
                    }
                }
                sequenceIdx++;
            }  // while ((sequenceIdx<combinations.size()) && (!targetFound)  // search the combinations within the same depth loop
            depth++;
        }  // while ((depth<=maxDepth) && (!targetFound))  // depth loop
        if(!targetFound) { 
            //#ifdef DEBUG
                std::cout << "[warning] ********** targetIdx[" << targetIdx << "]=" << target[targetIdx] << " not found within defined maxDepth. Appending lowestCostPath, LowestCost: "<< costOfLowestCostPath <<" ********** " << std::endl;
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

    rows=4; //setting wall parameters
    cols=4;
    sqAr.resize(rows*cols, 0.0); //setting number of changed square as zero

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
    if(!objPtr) {
        std::cerr << "[warning] object \"object\" does not exist." << std::endl;
    } else {
        #ifdef DEBUG
            std::cout << "[sucess] object \"object\" exists." << std::endl;
        #endif  // DEBUG
    }
    probot->Grab(objPtr);

    wallPtr = penv->GetKinBody("wall");
    if(!wallPtr) {
        std::cerr << "[warning] object \"wall\" does not exist." << std::endl;
    } else {
        #ifdef DEBUG
            std::cout << "[sucess] object \"wall\" exists." << std::endl;
        #endif  // DEBUG
    }

    usleep(1.0*pow(10,6));

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

    // Let's fill in the primitiveCollection for now.
        /*vector < vector<dReal> > primitive0;
        vector<dReal> primitive0step0(usedDof, 0.5);  // Eq. to {0.5, 0.5, 0.5}
        vector<dReal> primitive0step1(usedDof, 1.0);
        vector<dReal> primitive0step2(usedDof, 1.5);
        vector<dReal> primitive0step3(usedDof, 2.0);
        vector<dReal> primitive0step4(usedDof, 2.5);
        primitive0.push_back(primitive0step0);
        primitive0.push_back(primitive0step1);
        primitive0.push_back(primitive0step2);
        primitive0.push_back(primitive0step3);
        primitive0.push_back(primitive0step4);
        primitiveCollection.push_back(primitive0);

        vector < vector<dReal> > primitive1;
        vector<dReal> primitive1step0(usedDof, -0.5);
        vector<dReal> primitive1step1(usedDof, -1.0);
        vector<dReal> primitive1step2(usedDof, -1.5);
        vector<dReal> primitive1step3(usedDof, -2.0);
        vector<dReal> primitive1step4(usedDof, -2.5);
        primitive1.push_back(primitive1step0);
        primitive1.push_back(primitive1step1);
        primitive1.push_back(primitive1step2);
        primitive1.push_back(primitive1step3);
        primitive1.push_back(primitive1step4);
        primitiveCollection.push_back(primitive1);*/
    //

    // Let's fill in the primitiveCollection for now (a different example)
        /*vector < vector<dReal> > primitive0;
        vector<dReal> primitive0step0(usedDof, 0.0);  // Eq. to {0.0, 0.0, 0.0}
        primitive0step0[0] = 2.5;
        vector<dReal> primitive0step1(usedDof, 0.0);
        primitive0step1[0] = 5.0;
        vector<dReal> primitive0step2(usedDof, 0.0);
        primitive0step1[0] = 7.5;
        primitive0.push_back(primitive0step0);
        primitive0.push_back(primitive0step1);
        primitive0.push_back(primitive0step2);
        primitiveCollection.push_back(primitive0);

        vector < vector<dReal> > primitive1;
        vector<dReal> primitive1step0(usedDof, 0.0);  // Eq. to {0.0, 0.0, 0.0}
        primitive1step0[1] = 2.5;
        vector<dReal> primitive1step1(usedDof, 0.0);
        primitive1step1[1] = 5.0;
        vector<dReal> primitive1step2(usedDof, 0.0);
        primitive1step1[1] = 7.5;
        primitive1.push_back(primitive1step0);
        primitive1.push_back(primitive1step1);
        primitive1.push_back(primitive1step2);
        primitiveCollection.push_back(primitive1);

        vector < vector<dReal> > primitive2;
        vector<dReal> primitive2step0(usedDof, 0.0);  // Eq. to {0.0, 0.0, 0.0}
        primitive2step0[2] = 2.5;
        vector<dReal> primitive2step1(usedDof, 0.0);
        primitive2step1[2] = 5.0;
        vector<dReal> primitive2step2(usedDof, 0.0);
        primitive2step1[2] = 7.5;
        primitive2.push_back(primitive2step0);
        primitive2.push_back(primitive2step1);
        primitive2.push_back(primitive2step2);
        primitiveCollection.push_back(primitive2);

        vector < vector<dReal> > primitive3;
        vector<dReal> primitive3step0(usedDof, 0.0);  // Eq. to {0.0, 0.0, 0.0}
        primitive3step0[0] = -2.5;
        vector<dReal> primitive3step1(usedDof, 0.0);
        primitive3step1[0] = -5.0;
        vector<dReal> primitive3step2(usedDof, 0.0);
        primitive3step1[0] = -7.5;
        primitive3.push_back(primitive3step0);
        primitive3.push_back(primitive3step1);
        primitive3.push_back(primitive3step2);
        primitiveCollection.push_back(primitive3);

        vector < vector<dReal> > primitive4;
        vector<dReal> primitive4step0(usedDof, 0.0);  // Eq. to {0.0, 0.0, 0.0}
        primitive4step0[1] = -2.5;
        vector<dReal> primitive4step1(usedDof, 0.0);
        primitive4step1[1] = -5.0;
        vector<dReal> primitive4step2(usedDof, 0.0);
        primitive4step1[1] = -7.5;
        primitive4.push_back(primitive4step0);
        primitive4.push_back(primitive4step1);
        primitive4.push_back(primitive4step2);
        primitiveCollection.push_back(primitive4);

        vector < vector<dReal> > primitive5;
        vector<dReal> primitive5step0(usedDof, 0.0);  // Eq. to {0.0, 0.0, 0.0}
        primitive5step0[2] = -2.5;
        vector<dReal> primitive5step1(usedDof, 0.0);
        primitive5step1[2] = -5.0;
        vector<dReal> primitive5step2(usedDof, 0.0);
        primitive5step1[2] = -7.5;
        primitive5.push_back(primitive5step0);
        primitive5.push_back(primitive5step1);
        primitive5.push_back(primitive5step2);
        primitiveCollection.push_back(primitive5);*/
    //

    return true;
}

/************************************************************************/

double MotorPrimitives::compare(const vector<int>& sequence, const double& featureTarget) {

    vector<dReal> rawPoss(totalDof, 0.0);  // Start primitive from zero
    //rawPoss[18+0] += -15.0 * M_PI/180.0;  // Primitive in rad, pass to rad for openrave.
    //rawPoss[18+3] += -15.0 * M_PI/180.0;  // Primitive in rad, pass to rad for openrave.

    for(unsigned int primitiveIdx=0; primitiveIdx<sequence.size(); primitiveIdx++) {  // Perform the primitive.
        #ifdef DEBUG
            std::cout << "[info] * Perform sequence[primitiveIdx]: " << sequence[primitiveIdx] << std::endl;
        #endif  // DEBUG
        for(unsigned int stepIdx=0; stepIdx < primitiveCollection[sequence[primitiveIdx]].size(); stepIdx++) {  // Perform each step of the primitive.
            #ifdef DEBUG
                //std::cout << "[info] ** Perform stepIdx: " << stepIdx << std::endl;
            #endif  // DEBUG
            // primitiveCollection[primitiveIdx][stepIdx] is a vector<dReal>  // Add primitives sequentially
            rawPoss[18+0] += -1.0 * primitiveCollection[sequence[primitiveIdx]][stepIdx][0] * M_PI/180.0;  // Primitive in rad, pass to rad for openrave.
            rawPoss[18+1] += -1.0 * primitiveCollection[sequence[primitiveIdx]][stepIdx][1] * M_PI/180.0;  // Primitive in rad, pass to rad for openrave.
            rawPoss[18+3] += -1.0 * primitiveCollection[sequence[primitiveIdx]][stepIdx][2] * M_PI/180.0;  // Primitive in rad, pass to rad for openrave.
            probot->SetJointValues(rawPoss);
//            pcontrol->SetDesired(rawPoss); // This function "resets" physics ??
//            while(!pcontrol->IsDone()) {
//                boost::this_thread::sleep(boost::posix_time::milliseconds(1));
//            }
//            penv->StepSimulation(0.0001);  // StepSimulation must be given in seconds

            #ifdef DEBUG
                // draw the end effector of the trajectory
                vpoints.push_back(objPtr->GetTransform().trans);
                const float lineThickness = 4.0f;
                // const float lineColors[3] = {0,1,0};  // gominola
                const RaveVector< float > lineColors = RaveVector< float >(0, 0, 1, 1);
                pgraph = penv->drawlinestrip(&vpoints[0].x,vpoints.size(),sizeof(vpoints[0]),lineThickness,lineColors);
            #endif  // DEBUG

            T_base_object = objPtr->GetTransform();
            double T_base_object_x = T_base_object.trans.x;
            double T_base_object_y = T_base_object.trans.y;
            double T_base_object_z = T_base_object.trans.z;

            //change square color in function of dist (end-effector,square)
            for(int i=0; i<(rows*cols); i++){
                    stringstream ss;
                    ss << "square" << i;
                    Transform pos_square = wallPtr->GetLink(ss.str())->GetGeometry(0)->GetTransform();

                    double pos_square_x = pos_square.trans.x;
                    double pos_square_y = pos_square.trans.y;
                    double pos_square_z = pos_square.trans.z;
                    double dist = sqrt(pow(T_base_object_x-pos_square_x,2)
                                      + pow(T_base_object_y-pos_square_y,2)
                                      + pow(T_base_object_z-pos_square_z,2) );

                    if (dist < 0.12) {
                        #ifdef DEBUG
                            //j//wallPtr->GetLink(ss.str())->GetGeometry(0)->SetDiffuseColor(RaveVector<float>(0.0, 0.0, 1.0));  // draw it
                        #endif  // DEBUG
                        sqAr[i]=1;
                    }
                    ss.str("");
            }

            #ifdef DEBUG
                //usleep(0.1*pow(10,6));
            #endif  // DEBUG
        }  // Perform each step of the primitive.
    }  // Perform the primitive.

    int cSqAr[rows*cols];
    for(int i=0;i<rows*cols;i++)
        cSqAr[i] = sqAr[i];
    std::valarray<int> myvalarray(cSqAr,rows*cols);
    float percentage = ( (float)myvalarray.sum()/(rows*cols))*100;
    double cost = abs(percentage-featureTarget);
    #ifdef DEBUG
        std::cout << "[info] * sum: " << myvalarray.sum() << std::endl;
        std::cout << "[info] * percentage: " << percentage << std::endl;
        std::cout << "[info] * compare w.r.t. " << featureTarget <<  std::endl;
        std::cout << "[info] * cost (return value): " << cost <<  std::endl;
        vpoints.clear();
    #endif  // DEBUG
    return cost;
}
/************************************************************************/

