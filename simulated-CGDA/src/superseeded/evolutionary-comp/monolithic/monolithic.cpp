/*
 * First, monolithic version of the evolutionary search of CGDA: simulates the robot in
 * OpenRAVE and communicates through YARP. Superseded by ../evMono*.
 *
 * Part of the PhD thesis of Santiago Morante (Robotics Lab, Universidad Carlos III de Madrid).
 * Not updated since 2016: needs OpenRAVE and YARP.
 */

#include <openrave-core.h>
#include <vector>
#include <cstring>
#include <iostream>
#include <sstream>

#include <boost/thread/thread.hpp>
#include <boost/bind.hpp>

#include <yarp/os/all.h>
#include <yarp/dev/all.h>
#include <yarp/sig/all.h>

#include <yarp/math/Math.h>

#include "cv.h"

#include "TravisLib.hpp"
#include "TinyMath.hpp"

using namespace OpenRAVE;
using namespace std;

using namespace yarp::os;
using namespace yarp::sig::draw;

using namespace cv;

#define NUM_MOTORS    8.0

#define FX_D          64.0
#define FY_D          48.0
#define CX_D          64.0
#define CY_D          48.0
#define FX_RGB        64.0
#define FY_RGB        48.0
#define CX_RGB        64.0
#define CY_RGB        48.0

#define HEIGHT         512.0     // Base TransZ [mm]
#define PAN            0     // Base RotZ [deg]
#define TILT           -42.0     // Extra RotY [deg], neg looks down as in OpenNI, -42 goes good with real -50

void SetViewer(EnvironmentBasePtr penv, const string& viewername)
{
    ViewerBasePtr viewer = RaveCreateViewer(penv,viewername);
    BOOST_ASSERT(!!viewer);

    // attach it to the environment:
    penv->AttachViewer(viewer);

    // finally you call the viewer's infinite loop (this is why you need a separate thread):
    bool showgui = true;
    viewer->main(showgui);
    
}

int main(int argc, char ** argv) {

    Network yarp;
    if (!Network::checkNetwork()) {
        printf("Please start a yarp name server first\n");
        return(-1);
    }

    yarp::sig::Matrix H_0_c = rotZ(-90+PAN);
    H_0_c.resize(4,4);
    H_0_c(0,3)=0;
    H_0_c(1,3)=0;
    H_0_c(2,3)=0;
    H_0_c(3,0)=0;
    H_0_c(3,1)=0;
    H_0_c(3,2)=0;
    H_0_c(3,3)=1;
    printf("*** H_0_c *** \n(%s)\n\n", H_0_c.toString().c_str());

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
    printf("*** H_c_k *** \n(%s)\n\n", H_c_k.toString().c_str());

    yarp::sig::Matrix H_0_k = H_0_c * H_c_k;

    //int num = 1;
    string scenefilename = "../models/teo_action.env.xml";
    string viewername = "qtcoin";

    // parse the command line options
    int i = 1;
    while(i < argc) {
        if( strcmp(argv[i], "-h") == 0 || strcmp(argv[i], "-?") == 0 || strcmp(argv[i], "/?") == 0 || strcmp(argv[i], "--help") == 0 || strcmp(argv[i], "-help") == 0 ) {
            RAVELOG_INFO("orloadviewer [--num n] [--scene filename] viewername\n");
            return 0;
        }
        else if( strcmp(argv[i], "--scene") == 0 ) {
            scenefilename = argv[i+1];
            i += 2;
        }
        else
            break;
    }
    if( i < argc ) {
        viewername = argv[i++];
    }
    
    RaveInitialize(true); // start openrave core
    EnvironmentBasePtr penv = RaveCreateEnvironment(); // create the main environment
    RaveSetDebugLevel(Level_Debug);

    boost::thread thviewer(boost::bind(SetViewer,penv,viewername));
    penv->Load(scenefilename); // load the scene

    //-- Get Robot 0
    std::vector<RobotBasePtr> robots;
    penv->GetRobots(robots);
    std::cout << "Robot 0: " << robots.at(0)->GetName() << std::endl;  // default: teo
    RobotBasePtr probot = robots.at(0);
    
    KinBodyPtr objPtr = penv->GetKinBody("object");
    if(!objPtr) printf("[WorldRpcResponder] fail\n");
    probot->Grab(objPtr);

    
    //-- Get Robot 1's camera ptr, description and name
    std::vector<RobotBase::AttachedSensorPtr> sensors;
    sensors = robots.at(1)->GetAttachedSensors();

    SensorBasePtr psensorbaseL = sensors.at(0)->GetSensor();
    if(psensorbaseL == NULL) printf("[error] Bad sensorbaseL, may break in future because of this.\n");
    else printf("Good sensorbase...\n");
    std::string tipo = psensorbaseL->GetDescription();
    printf("%s\n",tipo.c_str());
    tipo = psensorbaseL->GetName();
    printf("%s\n",tipo.c_str());
    if (psensorbaseL->Supports(SensorBase::ST_Laser)) printf("[monolithic] success: Sensor 0 supports ST_Laser.\n");
    psensorbaseL->Configure(SensorBase::CC_PowerOn);
    psensorbaseL->Configure(SensorBase::CC_RenderDataOn);
    boost::shared_ptr<SensorBase::LaserSensorData> plasersensordata = boost::dynamic_pointer_cast<SensorBase::LaserSensorData>(psensorbaseL->CreateSensorData(SensorBase::ST_Laser));

    SensorBasePtr psensorbaseC = sensors.at(1)->GetSensor();
    if(psensorbaseC == NULL) printf("[error] Bad sensorbaseC, may break in future because of this.\n");
    else printf("Good sensorbase...\n");
    std::string tipo2 = psensorbaseC->GetDescription();
    printf("%s\n",tipo2.c_str());
    tipo = psensorbaseC->GetName();
    printf("%s\n",tipo2.c_str());
    if (psensorbaseC->Supports(SensorBase::ST_Camera)) printf("[monolithic] success: Sensor 1 supports ST_Camera.\n");
    psensorbaseC->Configure(SensorBase::CC_PowerOn);
    boost::shared_ptr<SensorBase::CameraGeomData> pcamerageomdata = boost::dynamic_pointer_cast<SensorBase::CameraGeomData>(psensorbaseC->GetSensorGeometry(SensorBase::ST_Camera));
    int cameraWidth = pcamerageomdata->width;
    int cameraHeight = pcamerageomdata->height;
    printf("Camera width: %d, height: %d.\n",cameraWidth,cameraHeight);
    boost::shared_ptr<SensorBase::CameraSensorData> pcamerasensordata = boost::dynamic_pointer_cast<SensorBase::CameraSensorData>(psensorbaseC->CreateSensorData(SensorBase::ST_Camera));

    psensorbaseC->SimulationStep(0.1);
    while( ! (pcamerasensordata->vimagedata.size() > 0 ) ) {
        psensorbaseC->GetSensorData(pcamerasensordata);
        printf("wait cam\n");
        Time::delay(.5);
    }

    BufferedPort<yarp::sig::ImageOf<yarp::sig::PixelRgb> > p_imagen;
    p_imagen.open("/monolithic/rgb:o");
    BufferedPort<yarp::sig::ImageOf<yarp::sig::PixelInt> > p_depth;
    p_depth.open("/monolithic/depth:o");
    RpcClient p_client;
    p_client.open("/monolithic/rpc:o");

    while(1) {

        std::vector<dReal> dEncRaw(NUM_MOTORS);
        dEncRaw[0] = (int(Time::now())%90)*M_PI/180.0;
        dEncRaw[1] = 0;
        dEncRaw[2] = 0;
        dEncRaw[3] = 0;
        dEncRaw[4] = 0;
        dEncRaw[5] = 0;
        dEncRaw[6] = 0;
        dEncRaw[7] = 0;
        probot->SetJointValues(dEncRaw);

        psensorbaseC->GetSensorData(pcamerasensordata);
        psensorbaseL->GetSensorData(plasersensordata);

        yarp::sig::ImageOf<yarp::sig::PixelRgb>& i_imagen = p_imagen.prepare(); 
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
        p_imagen.write();

        std::vector< RaveVector< dReal > > sensorRanges = plasersensordata->ranges;
        std::vector< RaveVector< dReal > > sensorPositions = plasersensordata->positions;
        Transform tinv = plasersensordata->__trans.inverse();
        yarp::sig::ImageOf<yarp::sig::PixelInt>& i_depth = p_depth.prepare();
        if(sensorRanges.size()==3072) i_depth.resize(64,48);  // Tamaño de la pantalla (64,48)
        else if(sensorRanges.size()==12288) i_depth.resize(128,96);
        else if(sensorRanges.size()==49152) i_depth.resize(256,192);
        else if(sensorRanges.size()==307200) i_depth.resize(640,480);
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
        p_depth.write();

        // {yarp ImageOf Rgb -> openCv Mat Bgr}
        IplImage *inIplImage = cvCreateImage(cvSize(cameraWidth, cameraHeight),
                                             IPL_DEPTH_8U, 3 );
        cvCvtColor((IplImage*)i_imagen.getIplImage(), inIplImage, CV_RGB2BGR);
        Mat inCvMat(inIplImage);
        Travis travis;    // ::Travis(quiet=true, overwrite=true);
        travis.setCvMat(inCvMat);
        travis.binarize("greenMinusRed", 30);
        travis.morphClosing( cameraWidth * 0.04 ); // 4 for 100, very rule-of-thumb
        travis.blobize(1);
        vector<cv::Point> blobsXY;
        travis.getBlobsXY(blobsXY);
        vector<double> blobsAngle, blobsArea;
        travis.getBlobsArea(blobsArea);
        bool ok = travis.getBlobsAngle(0,blobsAngle);  // method: 0=box, 1=ellipse; note check for return as 1 can break
        if (!ok) return -1;
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

        printf("%f %f %f %f %f\n",
            Time::now(),mmX_0,mmY_0,mmZ_0,blobsArea[0]);

    }

    /*
    // from <stdint.h>: typedef signed char int8_t
    //std::vector<uint8_t> currentFrame = pcamerasensordata->vimagedata;
    printf("Vector size: %d",pcamerasensordata->vimagedata.size()); // = 480 * 640 * 3 = 921600;
    printf(" ( %d * %d * 3 = %d )\n", imgw, imgh, imgw*imgh*3);
    printf("A blocking [cin] waiting for input before dumping camera image...\n");
    int null;
    cin >> null;
    for (int i_x = 0; i_x < imgw; ++i_x) {
      for (int i_y = 0; i_y < imgh; ++i_y) {
        printf("%d",pcamerasensordata->vimagedata[3*(i_x+(i_y*imgw))]); // r
        printf("%d",pcamerasensordata->vimagedata[1+3*(i_x+(i_y*imgw))]); // g
        printf("%d",pcamerasensordata->vimagedata[2+3*(i_x+(i_y*imgw))]); // b
      }
    }*/

    thviewer.join(); // wait for the viewer thread to exit
    penv->Destroy(); // destroy
    return 0;
}
