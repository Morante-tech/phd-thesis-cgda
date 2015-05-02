// -*- mode:C++; tab-width:3; c-basic-offset:4; indent-tabs-mode:nil -*-

#include "FunctionMinEvalOp.hpp"

//#define POINTS 2

/************************************************************************/

double FunctionMinEvalOp::getCustomFitness(vector <double> genPoints){
    //printf("begin: FunctionMinEvalOp::getCustomFitness()\n");

    std::vector<dReal> dEncRaw(probot->GetDOF());  // NUM_MOTORS

    double dEncRaw0 = genPoints[0]; 
    double dEncRaw1 = genPoints[1]; 
    double dEncRaw3 = genPoints[2]; 

    //dEncRaw[0] = genPoints[t*3+0]*M_PI/180.0;  // simple
    //dEncRaw[1] = genPoints[t*3+1]*M_PI/180.0;  // simple
    //dEncRaw[3] = genPoints[t*3+2]*M_PI/180.0;  // simple
    dEncRaw[0+18] = -dEncRaw0*M_PI/180.0 ;
    dEncRaw[1+18] = -dEncRaw1*M_PI/180.0 ;
    dEncRaw[3+18] = -dEncRaw3*M_PI/180.0 ;
    dEncRaw[4+18] = -45*M_PI/180.0;  // full
            
    probot->SetJointValues(dEncRaw);
    pcontrol->SetDesired(dEncRaw); // This function "resets" physics
    while(!pcontrol->IsDone()) {
        boost::this_thread::sleep(boost::posix_time::milliseconds(1));
    }

    penv->StepSimulation(0.0001);  // StepSimulation must be given in seconds        

    T_base_object = _objPtr->GetTransform();

    double T_base_object_x = T_base_object.trans.x*1000.0;  // Pass to mm.
    double T_base_object_y = T_base_object.trans.y*1000.0;  // Pass to mm.
    double T_base_object_z = T_base_object.trans.z*1000.0;  // Pass to mm.

        T_base_target_x = T_base_kinect.trans.x*1000.0 - targetX;
        T_base_target_y = T_base_kinect.trans.y*1000.0 - targetY;
        T_base_target_z = T_base_kinect.trans.z*1000.0 - targetZ;

 //   printf("%.2f %.2f %.2f | %.2f %.2f %.2f | %.2f %.2f %.2f | %.2f %.2f %.2f.\n",
  //              targetX, targetY, targetZ,
   //             T_base_target_x,T_base_target_x,T_base_target_z,
     //           dEncRaw0,dEncRaw1,dEncRaw3,
       //         T_base_object_x,T_base_object_y,T_base_object_z);

    double fit = sqrt ( pow(T_base_object_x-T_base_target_x,2) + pow(T_base_object_y-T_base_target_y,2) + pow(T_base_object_z-T_base_target_z,2) );
    
 //   printf("fit: %f\n\n", fit);

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

