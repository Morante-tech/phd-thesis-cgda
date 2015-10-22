// -*- mode:C++; tab-width:3; c-basic-offset:4; indent-tabs-mode:nil -*-

#include "FunctionMinEvalOp.hpp"

/************************************************************************/

double FunctionMinEvalOp::getCustomFitness(vector <double> genPoints){
    //printf("begin: FunctionMinEvalOp::getCustomFitness()\n");

    //Bottle complete, fitness;
    //complete.clear();
    //fitness.clear();

//    for(int t=0;t<10;t++) {

            std::vector<dReal> dEncRaw(probot->GetDOF());  // NUM_MOTORS
            //dEncRaw[0] = genPoints[t*3+0]*M_PI/180.0;  // simple
            //dEncRaw[1] = genPoints[t*3+1]*M_PI/180.0;  // simple
            //dEncRaw[3] = genPoints[t*3+2]*M_PI/180.0;  // simple
            dEncRaw[0+18] = -genPoints[0]*M_PI/180.0;  // full
            dEncRaw[1+18] = -genPoints[1]*M_PI/180.0;  // full
            dEncRaw[3+18] = -genPoints[2]*M_PI/180.0;  // full
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

            double T_base_object_x = T_base_object.trans.x*1000.0;  // Pass to mm.
            double T_base_object_y = T_base_object.trans.y*1000.0;  // Pass to mm.
            double T_base_object_z = T_base_object.trans.z*1000.0;  // Pass to mm.

            double T_kinect_object_x = (T_base_kinect.trans.x-T_base_object.trans.x)*1000.0;  // Pass to mm.
            double T_kinect_object_y = (T_base_kinect.trans.y-T_base_object.trans.y)*1000.0;  // Pass to mm.
            double T_kinect_object_z = (T_base_object.trans.z)*1000.0;  // Pass to mm.

            //printf("%d: %f %f %f | b_o %2.4f %2.4f %2.4f | k_o %2.4f %2.4f %2.4f.\n", t, genPoints[t*3+0],genPoints[t*3+1],genPoints[t*3+2],
            //    T_base_object_x, T_base_object_y, T_base_object_z, T_kinect_object_x, T_kinect_object_y, T_kinect_object_z);

            printf("%f %f %f | b_o %2.4f %2.4f %2.4f | k_o %2.4f %2.4f %2.4f.\n", genPoints[0],genPoints[1],genPoints[2],
                T_base_object_x, T_base_object_y, T_base_object_z, T_kinect_object_x, T_kinect_object_y, T_kinect_object_z);
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

 //   }

   // effectsClient->write(complete,fitness);
    //double fit = floorf( (fitness.get(0).asDouble() * 10.0) + 0.5) / 10.0;
    //double fit = fitness.get(0).asDouble();
    //
    //double target[3] = {6.38762472700000e+02,2.72626977500000e+00,-3.97845084999999e+00};  // 23.7698	28.6428	17.2571
    //double target[3] = {6.42391811965000e+02,1.68573559950000e+01,-3.02628304000000e+00};  // 23.5782	29.8498	16.9078
    //double target[3] = {6.80641917184079e+02,8.88397871243782e+01,1.23043924875622e+00};  // 26.4691	35.7294	6.06159
    double target[3] = {7.83047694335000e+02,1.20799710345000e+02,6.47513742499999e+00};  // 5.25326	42.1344	24.2452
    double fit = sqrt( pow(T_kinect_object_x-target[0],2) + pow(T_kinect_object_y-target[1],2) + pow(T_kinect_object_z-target[2],2) );
    printf("Got fit: %f\n\n", fit);

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

