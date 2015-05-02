// -*- mode:C++; tab-width:3; c-basic-offset:4; indent-tabs-mode:nil -*-

#include "FunctionMinEvalOp.hpp"

/************************************************************************/

double FunctionMinEvalOp::getCustomFitness(vector <double> genPoints){
    printf("begin: FunctionMinEvalOp::getCustomFitness()\n");

    yarp::sig::Matrix H_0_c = rotZ(-90+PAN);
    H_0_c.resize(4,4);
    H_0_c(0,3)=0;
    H_0_c(1,3)=0;
    H_0_c(2,3)=0;
    H_0_c(3,0)=0;
    H_0_c(3,1)=0;
    H_0_c(3,2)=0;
    H_0_c(3,3)=1;
    //printf("*** H_0_c *** \n(%s)\n\n", H_0_c.toString().c_str());

    yarp::sig::Matrix H_c_k = rotX(-90.0+TILT);
    H_c_k.resize(4,4);
    //
    H_c_k(0,3)=0;
    H_c_k(1,3)=0;
    H_c_k(2,3)=0;
    H_c_k(3,0)=0;
    H_c_k(3,1)=0;
    H_c_k(3,2)=0;
    //
    H_c_k(2,3)=HEIGHT;
    H_c_k(3,3)=1;
    //printf("*** H_c_k *** \n(%s)\n\n", H_c_k.toString().c_str());

    yarp::sig::Matrix H_0_k = H_0_c * H_c_k;

    Bottle complete, fitness;
    complete.clear();
    fitness.clear();
    //complete.addString("real");

    for(int t=0;t<10;t++) {

            std::vector<dReal> dEncRaw(NUM_MOTORS);
            //dEncRaw[0] = (int(Time::now())%90)*M_PI/180.0;
            dEncRaw[0] = genPoints[t*3+0]*M_PI/180.0;
            dEncRaw[1] = genPoints[t*3+1]*M_PI/180.0;
            dEncRaw[2] = 0;
            dEncRaw[3] = genPoints[t*3+2]*M_PI/180.0;
            dEncRaw[4] = 0;
            dEncRaw[4] = 0;
            dEncRaw[5] = 0;
            dEncRaw[6] = 0;
            dEncRaw[7] = 0;
            
            //penv->StepSimulation(.01);  // StepSimulation must be given in seconds
            //probot->SetJointValues(dEncRaw);
            pcontrol->SetDesired(dEncRaw); // This function "resets" physics
            //probot->WaitForController(0)
            //while(!pcontrol->IsDone()) {
            //    boost::this_thread::sleep(boost::posix_time::milliseconds(1));
            //}

            //penv->StepSimulation(.0001);  // StepSimulation must be given in seconds
            psensorbaseC->SimulationStep(.0000001);
            //psensorbaseL->SimulationStep(.00001);
            
            psensorbaseC->GetSensorData(pcamerasensordata);
            psensorbaseL->GetSensorData(plasersensordata);

            yarp::sig::ImageOf<yarp::sig::PixelRgb>& i_imagen = p_imagen->prepare(); 
            i_imagen.resize(cameraWidth,cameraHeight);  // Tamaño de la pantalla
            yarp::sig::PixelRgb p;
            for (int i_x = 0; i_x < cameraWidth; ++i_x) {
                for (int i_y = 0; i_y < cameraHeight; ++i_y) {
                    p.r = pcamerasensordata->vimagedata[3*(i_x+(i_y*cameraWidth))];
                    p.g = pcamerasensordata->vimagedata[1+3*(i_x+(i_y*cameraWidth))];
                    p.b = pcamerasensordata->vimagedata[2+3*(i_x+(i_y*cameraWidth))];
                    i_imagen.safePixel(i_x,i_y) = p;
                }
            }
            //p_imagen->write();

            std::vector< RaveVector< dReal > > sensorRanges = plasersensordata->ranges;
            std::vector< RaveVector< dReal > > sensorPositions = plasersensordata->positions;
            Transform tinv = plasersensordata->__trans.inverse();
            yarp::sig::ImageOf<yarp::sig::PixelInt>& i_depth = p_depth->prepare();
            if(sensorRanges.size()==3072) i_depth.resize(64,48);  // Tamaño de la pantalla (64,48)
            else if(sensorRanges.size()==12288) i_depth.resize(128,96);
            else if(sensorRanges.size()==49152) i_depth.resize(256,192);
            //else if(sensorRanges.size()==307200) i_depth.resize(640,480);
            else if(sensorRanges.size()==4) i_depth.resize(2,2);
            //else printf("[warning] unrecognized laser sensor data size.\n");
            else i_depth.resize(sensorRanges.size(),1);
            for (int i_y = 0; i_y < i_depth.height(); ++i_y) {  // was y in x before
                for (int i_x = 0; i_x < i_depth.width(); ++i_x) {
                    //double p = sensorRanges[i_y+(i_x*i_depth.height())].z;
                    double p;
                    if( sensorPositions.size() > 0 ) {
                        OpenRAVE::Vector v = tinv*(sensorRanges[i_y+(i_x*i_depth.height())] + sensorPositions[0]);
                        p = (float)v.z;
                    } else {
                        OpenRAVE::Vector v = tinv*(sensorRanges[i_y+(i_x*i_depth.height())]);
                        p = (float)v.z;
                    }
                    i_depth(i_x,i_y) = p*1000.0;  // give mm
                }
            }
            //p_depth->write();

            // {yarp ImageOf Rgb -> openCv Mat Bgr}
            IplImage *inIplImage = cvCreateImage(cvSize(cameraWidth, cameraHeight),
                                             IPL_DEPTH_8U, 3 );
            cvCvtColor((IplImage*)i_imagen.getIplImage(), inIplImage, CV_RGB2BGR);
            Mat inCvMat(inIplImage);
            Travis travis;    // ::Travis(quiet=true, overwrite=true);
            bool ok = travis.setCvMat(inCvMat);
            ok &= travis.binarize("greenMinusRed", 30);
            travis.morphClosing( cameraWidth * 0.04 ); // 4 for 100, very rule-of-thumb
            travis.blobize(1);
            vector<cv::Point> blobsXY;
            ok &= travis.getBlobsXY(blobsXY);
            vector<double> blobsAngle, blobsArea;
            vector<double> blobsHue,blobsSat,blobsVal,blobsHueStdDev,blobsSatStdDev,blobsValStdDev;
            ok &= travis.getBlobsArea(blobsArea);
            ok &= travis.getBlobsHSV(blobsHue,blobsSat,blobsVal,blobsHueStdDev,blobsSatStdDev,blobsValStdDev);
            ok &= travis.getBlobsAngle(0,blobsAngle);  // method: 0=box, 1=ellipse; note check for return as 1 can break
            if (!ok) {
                printf("[warning] travis error !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n");
                return 100000000.0;
            }
            Mat outCvMat = travis.getCvMat(0,3);
            travis.release();
            // { openCv Mat Bgr -> yarp ImageOf Rgb}
            IplImage outIplImage = outCvMat;
            cvCvtColor(&outIplImage,&outIplImage, CV_BGR2RGB);
            char sequence[] = "RGB";
            strcpy (outIplImage.channelSeq,sequence);
            yarp::sig::ImageOf<yarp::sig::PixelRgb> outYarpImg;
            outYarpImg.wrapIplImage(&outIplImage);
            yarp::sig::PixelRgb blue(0,0,255);
            addCircle(outYarpImg,blue,blobsXY[0].x,blobsXY[0].y,3);

            double mmZ = i_depth.pixel(int(blobsXY[0].x),int(blobsXY[0].y));
            double mmX = 1000.0 * ( (blobsXY[0].x - CX_D) * mmZ/1000.0 ) / FX_D;
            double mmY = 1000.0 * ( (blobsXY[0].y - CY_D) * mmZ/1000.0 ) / FY_D;

            yarp::sig::Matrix X_k_P(4,1);
            X_k_P(0,0)=mmX;
            X_k_P(1,0)=mmY;
            X_k_P(2,0)=mmZ;
            X_k_P(3,0)=1;
            yarp::sig::Matrix X_0_P = H_0_k * X_k_P;
            if (mmZ < 0.001) {
                X_0_P(0,0) = -9999;
                X_0_P(1,0) = -9999;
                X_0_P(2,0) = -9999;
            }
            double mmX_0 = X_0_P(0,0);
            double mmY_0 = X_0_P(1,0);
            double mmZ_0 = X_0_P(2,0);

        /*printf("%f %f %f | %f %f | %f %f %f\n",
            blobsXY[0].x-(cameraWidth/2.0), blobsXY[0].y-(cameraHeight/2.0),mmZ,
            mmX,mmY,
            mmX_0,mmY_0,mmZ_0);*/

        /*printf("%f %f %f %f %f\n",
            Time::now(),mmX_0,mmY_0,mmZ_0,blobsArea[0]);*/
            Bottle part;
            part.clear();
            //part.addDouble(Time::now());
            //part.addDouble(t+Time::now());
            part.addDouble(1+t/2.0);
            part.addDouble(mmX_0);
            part.addDouble(mmY_0);
            part.addDouble(mmZ_0);
/*            part.addDouble(blobsArea[0]);
            part.addDouble(blobsHue[0]);
            part.addDouble(blobsSat[0]);
            part.addDouble(blobsVal[0]);
            part.addDouble(blobsAngle[0]);*/
            printf("Part %d: %s\n",t,part.toString().c_str());
            complete.addList() = part;        
            printf("Part added.\n");

            cvReleaseImage( &inIplImage );  // release the memory for the image
            outCvMat.release();  // cvReleaseImage( &outIplImage );  // release the memory for the image

    }


    //effectsClient->write(complete);
    printf("Write complete: %s\nand wait for fitness...\n",complete.toString().c_str());
    //effectsClient->read(fitness);
    //printf("\nGot fitness: %s.\n", fitness.toString().c_str());
    //double fit = fitness.get(0).asDouble();
    /////printf("Got fit: %f\n", fit);
    effectsClient->write(complete,fitness);
    double fit = fitness.get(0).asDouble();
    printf("Got fit: %f\n", fit);

    printf("end: FunctionMinEvalOp::getCustomFitness()\n");

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

