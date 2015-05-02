// -*- mode:C++; tab-width:3; c-basic-offset:4; indent-tabs-mode:nil -*-

#include "FunctionMinEvalOp.hpp"

//#define POINTS 2

/************************************************************************/

double FunctionMinEvalOp::getCustomFitness(vector <double> genPoints){
    //printf("begin: FunctionMinEvalOp::getCustomFitness()\n");

    //Bottle complete, fitness;
    //complete.clear();
    //fitness.clear();

    double T_kinect_object_x;
    double T_kinect_object_y;
    double T_kinect_object_z;

    //for(int t=0;t<POINTS;t++) {

            std::vector<dReal> dEncRaw(probot->GetDOF());  // NUM_MOTORS
            //dEncRaw[0] = genPoints[t*3+0]*M_PI/180.0;  // simple
            //dEncRaw[1] = genPoints[t*3+1]*M_PI/180.0;  // simple
            //dEncRaw[3] = genPoints[t*3+2]*M_PI/180.0;  // simple
            double dEncRaw0 = genPoints[0]; 
            double dEncRaw1 = genPoints[1]; 
            double dEncRaw3 = genPoints[2]; 

            dEncRaw[0+18] = -dEncRaw0*M_PI/180.0 ;
            dEncRaw[1+18] = -dEncRaw1*M_PI/180.0 ;
            dEncRaw[3+18] = -dEncRaw3*M_PI/180.0 ;

    dEncRaw[4+18] = -45*M_PI/180.0;  // full
            
            //penv->StepSimulation(.01);  // StepSimulation must be given in seconds
            probot->SetJointValues(dEncRaw);
            //probot->WaitForController(0);
            pcontrol->SetDesired(dEncRaw); // This function "resets" physics
            while(!pcontrol->IsDone()) {
                boost::this_thread::sleep(boost::posix_time::milliseconds(1));
            }

            penv->StepSimulation(0.0001);  // StepSimulation must be given in seconds
            

            T_base_object = _objPtr->GetTransform();

            T_kinect_object_x = (T_base_kinect.trans.x-T_base_object.trans.x)*1000.0;  // Pass to mm.
            T_kinect_object_y = (T_base_kinect.trans.y-T_base_object.trans.y)*1000.0;  // Pass to mm.
            T_kinect_object_z = (T_base_object.trans.z)*1000.0;  // Pass to mm.

            //printf("%d: %f %f %f | b_o %2.4f %2.4f %2.4f | k_o %2.4f %2.4f %2.4f.\n", t, genPoints[t*3+0],genPoints[t*3+1],genPoints[t*3+2],
            //    T_base_object_x, T_base_object_y, T_base_object_z, T_kinect_object_x, T_kinect_object_y, T_kinect_object_z);

            printf("%f %f %f | %f %f %f | k_o %2.4f %2.4f %2.4f.\n", targetX, targetY, targetZ, dEncRaw0,dEncRaw1,dEncRaw3,
                T_kinect_object_x, T_kinect_object_y, T_kinect_object_z);
            //usleep(1.0 * 1000000.0);

        /*printf("%f %f %f %f %f\n",
            Time::now(),mmX_0,mmY_0,mmZ_0,blobsArea[0]);*/
/*            Bottle part;
            part.clear();
            //part.addDouble(Time::now());
            //part.addDouble(t+Time::now());
            part.addDouble(1+t/2.0);
            part.addDouble( T_kinect_object_x );
            part.addDouble( T_kinect_object_y );
            part.addDouble( T_kinect_object_z );*/
            //printf("Part %d: %s\n",t,part.toString().c_str());
//            complete.addList() = part;        
            //printf("Part added.\n");

    //}

   // effectsClient->write(complete,fitness);
    //double fit = floorf( (fitness.get(0).asDouble() * 10.0) + 0.5) / 10.0;
    //double fit = fitness.get(0).asDouble();
    //
    //double target[3*POINTS] = {6.38762472700000e+02,2.72626977500000e+00,-3.97845084999999e+00,
    //                           6.42391811965000e+02,1.68573559950000e+01,-3.02628304000000e+00};


    double fit = sqrt ( pow(T_kinect_object_x-targetX,2) + pow(T_kinect_object_y-targetY,2) + pow(T_kinect_object_z-targetZ,2) );
    
    //fit += pow(T_kinect_object_x[0]-target[0],2) + pow(T_kinect_object_y[0]-target[1],2) + pow(T_kinect_object_z[0]-target[2],2);
    //fit += pow(T_kinect_object_x[1]-target[3],2) + pow(T_kinect_object_y[1]-target[4],2) + pow(T_kinect_object_z[1]-target[5],2);
          
    printf("fit: %f\n\n", fit);

    //printf("end: FunctionMinEvalOp::getCustomFitness()\n");

    return fit;
    //return fitness.get(0).asDouble();
}

/************************************************************************/

void FunctionMinEvalOp::registerParameters(StateP state) {
	state->getRegistry()->registerEntry("function", (voidP) (new uint(1)), ECF::UINT);
}

/************************************************************************/

bool FunctionMinEvalOp::initialize(StateP state) {

	voidP sptr = state->getRegistry()->getEntry("function"); // get parameter value

    _objPtr = penv->GetKinBody("object");
    if(!_objPtr) {
        fprintf(stderr,"error: object \"object\" does not exist.\n");
    } else printf("sucess: object \"object\" exists.\n");
    T_base_object = _objPtr->GetTransform();
    printf("object \"object\" at %f %f %f.\n", T_base_object.trans.x, T_base_object.trans.y, T_base_object.trans.z);

    KinBodyPtr _kinectPtr = penv->GetKinBody("kinect");
    if(!_kinectPtr) {
        fprintf(stderr,"error: object \"kinect\" does not exist.\n");
    } else printf("sucess: object \"kinect\" exists.\n");
    T_base_kinect = _kinectPtr->GetTransform();
    printf("object \"kinect\" at %f %f %f.\n", T_base_kinect.trans.x, T_base_kinect.trans.y, T_base_kinect.trans.z);

            usleep(1.0 * 1000000.0);

	return true;
}

/************************************************************************/

FitnessP FunctionMinEvalOp::evaluate(IndividualP individual) {

	// evaluation creates a new fitness object using a smart pointer
	// in our case, we try to minimize the function value, so we use FitnessMin fitness (for minimization problems)
	FitnessP fitness (new FitnessMin);

	// we define FloatingPoint as the only genotype (in the configuration file)
	FloatingPoint::FloatingPoint* gen = (FloatingPoint::FloatingPoint*) individual->getGenotype().get();

	// we implement the fitness function 'as is', without any translation
	// the number of variables is read from the genotype itself (size of 'realValue' vactor)

    double value =0;
    value= getCustomFitness(gen->realValue);

	fitness->setValue(value);
	return fitness;
}

/************************************************************************/

