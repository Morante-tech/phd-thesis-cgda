// -*- mode:C++; tab-width:3; c-basic-offset:4; indent-tabs-mode:nil -*-

#include "FunctionMinEvalOp.hpp"

/************************************************************************/

double FunctionMinEvalOp::getCustomFitness(vector <double> genPoints){
    //printf("begin: FunctionMinEvalOp::getCustomFitness()\n");

    Bottle complete, fitness;
    complete.clear();
    fitness.clear();
    //complete.addString("real");

    for(int t=0;t<10;t++) {

            std::vector<dReal> dEncRaw(probot->GetDOF());  // NUM_MOTORS
            //dEncRaw[0] = genPoints[t*3+0]*M_PI/180.0;  // simple
            //dEncRaw[1] = genPoints[t*3+1]*M_PI/180.0;  // simple
            //dEncRaw[3] = genPoints[t*3+2]*M_PI/180.0;  // simple
            dEncRaw[0+18] = -genPoints[t*3+0]*M_PI/180.0;  // full
            dEncRaw[1+18] = -genPoints[t*3+1]*M_PI/180.0;  // full
            dEncRaw[3+18] = -genPoints[t*3+2]*M_PI/180.0;  // full
    dEncRaw[4+18] = -45*M_PI/180.0;  // full
            
            //penv->StepSimulation(.01);  // StepSimulation must be given in seconds
            //probot->SetJointValues(dEncRaw);
            pcontrol->SetDesired(dEncRaw); // This function "resets" physics
            //probot->WaitForController(0)
            //while(!pcontrol->IsDone()) {
            //    boost::this_thread::sleep(boost::posix_time::milliseconds(1));
            //}

            //double T_base_object_x = T_base_object.trans.x*1000.0;  // Pass to mm.
            //double T_base_object_y = T_base_object.trans.y*1000.0;  // Pass to mm.
            //double T_base_object_z = T_base_object.trans.z*1000.0;  // Pass to mm.

            T_base_object = _objPtr->GetTransform();

            double T_kinect_object_x = (T_base_kinect.trans.x-T_base_object.trans.x)*1000.0;  // Pass to mm.
            double T_kinect_object_y = (T_base_kinect.trans.y-T_base_object.trans.y)*1000.0;  // Pass to mm.
            double T_kinect_object_z = (T_base_object.trans.z)*1000.0;  // Pass to mm.

            //printf("%d: %f %f %f | b_o %2.4f %2.4f %2.4f | k_o %2.4f %2.4f %2.4f.\n", t, genPoints[t*3+0],genPoints[t*3+1],genPoints[t*3+2],
            //    T_base_object_x, T_base_object_y, T_base_object_z, T_kinect_object_x, T_kinect_object_y, T_kinect_object_z);

        /*printf("%f %f %f %f %f\n",
            Time::now(),mmX_0,mmY_0,mmZ_0,blobsArea[0]);*/
            Bottle part;
            part.clear();
            //part.addDouble(Time::now());
            //part.addDouble(t+Time::now());
            part.addDouble(1+t/2.0);
            part.addDouble( T_kinect_object_x );
            part.addDouble( T_kinect_object_y );
            part.addDouble( T_kinect_object_z );
/*            part.addDouble(blobsArea[0]);
            part.addDouble(blobsHue[0]);
            part.addDouble(blobsSat[0]);
            part.addDouble(blobsVal[0]);
            part.addDouble(blobsAngle[0]);*/
            //printf("Part %d: %s\n",t,part.toString().c_str());
            complete.addList() = part;        
            //printf("Part added.\n");

    }

    effectsClient->write(complete,fitness);
    //double fit = floorf( (fitness.get(0).asDouble() * 10.0) + 0.5) / 10.0;
    double fit = fitness.get(0).asDouble();
    printf("Got fit: %f\n", fit);

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

