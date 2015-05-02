// -*- mode:C++; tab-width:3; c-basic-offset:4; indent-tabs-mode:nil -*-

#include "FunctionMinEvalOp.hpp"
#include <sstream>
#include <string>
#include <vector>
#include <valarray>     // std::valarray

#include <opencv2/opencv.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <opencv2/core/core.hpp>
/************************************************************************/

//class OpenRAVECamera
//{
//public:
//    OpenRAVECamera(SensorBasePtr psensor)
//    {
//        pcamera=psensor;
//        pdata = boost::static_pointer_cast<SensorBase::CameraSensorData>(pcamera->CreateSensorData(SensorBase::ST_Camera));
//        geom = *boost::static_pointer_cast<SensorBase::CameraGeomData>(pcamera->GetSensorGeometry(SensorBase::ST_Camera));
//        img = cvCreateImage(cvSize(geom.width,geom.height),IPL_DEPTH_8U,3);
//    }
//    virtual ~OpenRAVECamera() {
//        cvReleaseImage(&img);
//    }

//    SensorBasePtr pcamera;
//    SensorBase::CameraGeomData geom;
//    boost::shared_ptr<SensorBase::CameraSensorData> pdata;
//    IplImage* img;
//};

double target[5]={0, 10, 40, 80, 100};


double FunctionMinEvalOp::getCustomFitness(vector <double> genPoints){

     // // reset square color for opencv
//    for(int i=0; i<4; i++){
//        for(int j=0; j<4; j++){
//            stringstream rr;
//            rr << "square" << i << j;
//            _wall->GetLink(rr.str())->GetGeometry(0)->SetDiffuseColor(RaveVector<float>(0.5, 0.5, 0.5));
//            rr.str("");
//        }}

    const int rows=4; //setting wall parameters
    const int cols=4;
    const int numbPoints=5;
    float percentage[numbPoints];
    int sqAr [rows*cols] = { }; //setting number of changed square as cero

    for(int t=0;t<numbPoints;t++) {
        //things about moving arm
        std::vector<dReal> dEncRaw(probot->GetDOF());  // NUM_MOTORS
        dEncRaw[0+18] = -genPoints[t*3+0]*M_PI/180.0;  // simple
        dEncRaw[1+18] = -genPoints[t*3+1]*M_PI/180.0;  // simple
        dEncRaw[3+18] = -genPoints[t*3+2]*M_PI/180.0;  // simple
        dEncRaw[4+18] = -45*M_PI/180.0;

        probot->SetJointValues(dEncRaw);
        pcontrol->SetDesired(dEncRaw); // This function "resets" physics
        while(!pcontrol->IsDone()) {
            boost::this_thread::sleep(boost::posix_time::milliseconds(1));
        }

        penv->StepSimulation(0.0001);  // StepSimulation must be given in seconds
        T_base_object = _objPtr->GetTransform();
        double T_base_object_x = T_base_object.trans.x;
        double T_base_object_y = T_base_object.trans.y;
        double T_base_object_z = T_base_object.trans.z;

        //change square color in function of dist (end-effector,square)
        for(int i=0; i<(rows*cols); i++){
                stringstream ss;
                ss << "square" << i;
                Transform pos_square = _wall->GetLink(ss.str())->GetGeometry(0)->GetTransform();

                double pos_square_x = pos_square.trans.x;
                double pos_square_y = pos_square.trans.y;
                double pos_square_z = pos_square.trans.z;
                double dist = sqrt(pow(T_base_object_x-pos_square_x,2)
                                  + pow(T_base_object_y-pos_square_y,2)
                                  + pow(T_base_object_z-pos_square_z,2) );

                if (dist < 0.12){
//                    _wall->GetLink(ss.str())->GetGeometry(0)->SetDiffuseColor(RaveVector<float>(0.0, 0.0, 1.0));
                    sqAr[i]=1;
                }
                ss.str("");
        }

        //opencv etc
    // BEGIN->AQUI EXTRAER IMAGEN CAMARA!!!

    //    // extract all the cameras
    //    std::vector<SensorBasePtr> allsensors;
    //    penv->GetSensors(allsensors);
    //    std::vector< boost::shared_ptr<OpenRAVECamera> > vcameras;
    //    for( std::vector<SensorBasePtr>::iterator itsensor = allsensors.begin(); itsensor != allsensors.end(); ++itsensor) {
    //        if( (*itsensor)->Supports(SensorBase::ST_Camera) ) {
    //            (*itsensor)->Configure(SensorBase::CC_PowerOn);
    //            (*itsensor)->Configure(SensorBase::CC_RenderDataOn);
    //            vcameras.push_back(boost::shared_ptr<OpenRAVECamera>(new OpenRAVECamera(*itsensor)));
    //        }
    //    }

    //        for(size_t icamera = 0; icamera < vcameras.size(); ++icamera) {
    //            vcameras[icamera]->pcamera->GetSensorData(vcameras[icamera]->pdata);
    //            if( vcameras[icamera]->pdata->vimagedata.size() > 0 ) {
    //                char* imageData = vcameras[icamera]->img->imageData;
    //                uint8_t* src = &vcameras[icamera]->pdata->vimagedata.at(0);
    //                for(int i=0; i < vcameras[icamera]->geom.height; i++, imageData += vcameras[icamera]->img->widthStep, src += 3*vcameras[icamera]->geom.width) {
    //                    for(int j=0; j<vcameras[icamera]->geom.width; j++) {
    //                        // opencv is bgr while openrave is rgb
    //                        imageData[3*j] = src[3*j+2];
    //                        imageData[3*j+1] = src[3*j+1];
    //                        imageData[3*j+2] = src[3*j+0];
    //                    }
    //                }
    //            }
    //        }

    // END->AQUI EXTRAER IMAGEN CAMARA!!!

     std::valarray<int> myvalarray (sqAr,rows*cols);
     percentage[t]= ( (float)myvalarray.sum()/(rows*cols))*100;

//     cout << std::endl << " d: " << myvalarray.sum() << " " << percentage[t] << " ";
    } //cierre bucle trayectoria completa


    //Ahora mismo fitness manipulado
    // calculate fit /percentage of painted wall
    double fit = sqrt(pow(percentage[0]-target[0],2)
                    + pow(percentage[1]-target[1],2)
                    + pow(percentage[2]-target[2],2)
                    + pow(percentage[3]-target[3],2)
                    + pow(percentage[4]-target[4],2) );

  //  cout << std::endl << " percentage: "<< percentage[0] << ","<< percentage[1] << ","<< percentage[2] << ","<< percentage[3] << ","<< percentage[4];
    cout << std::endl << " fit: " << fit << " ";
    return fit;
}

/************************************************************************/

void FunctionMinEvalOp::registerParameters(StateP state) {
	state->getRegistry()->registerEntry("function", (voidP) (new uint(1)), ECF::UINT);
}

/************************************************************************/

bool FunctionMinEvalOp::initialize(StateP state) {

	voidP sptr = state->getRegistry()->getEntry("function"); // get parameter value
    stringstream msg;
    _objPtr = penv->GetKinBody("object");
    _wall = penv->GetKinBody("wall");

    if(!_objPtr) {
        fprintf(stderr,"error: object \"object\" does not exist.\n");
    } else printf("sucess: object \"object\" exists.\n");

    if(!_wall) {
        fprintf(stderr,"error: object \"wall\" does not exist.\n");
    } else printf("sucess: object \"wall\" exists.\n");


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

