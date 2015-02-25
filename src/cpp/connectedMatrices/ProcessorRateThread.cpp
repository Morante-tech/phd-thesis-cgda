// -*- mode:C++; tab-width:4; c-basic-offset:4; indent-tabs-mode:nil -*-

#include "ProcessorRateThread.hpp"

/************************************************************************/
bool teo::ProcessorRateThread::threadInit() {

    while( inYarpImg1.width() < 1 ) {
        iFrameGrabberImage1->getImage(inYarpImg1);
        CD_INFO("Wait for iFrameGrabberImage1...\n");
        yarp::os::Time::delay(0.5);
    }
    while( inYarpImg2.width() < 1 ) {
        iFrameGrabberImage2->getImage(inYarpImg2);
        CD_INFO("Wait for iFrameGrabberImage2...\n");
        yarp::os::Time::delay(0.5);
    }
    printf("iFrameGrabberImage1 got a %dx%d image\n", inYarpImg1.width(), inYarpImg1.height());
    printf("iFrameGrabberImage2 got a %dx%d image\n", inYarpImg2.width(), inYarpImg2.height());

    int frame1Rows = inYarpImg1.height();
    int frame1Cols = inYarpImg1.width();
    int frame2Rows = inYarpImg2.height();
    int frame2Cols = inYarpImg2.width();

    COLS_1 = ROWS_1 * frame1Cols / frame1Rows;
    COLS_2 = ROWS_2 * frame2Cols / frame2Rows;

    inCvImg1 = cvCreateImage(cvSize(inYarpImg1.width(),
                             inYarpImg1.height()),
                             IPL_DEPTH_8U, 1 );

    inCvImg2 = cvCreateImage(cvSize(inYarpImg2.width(),
                             inYarpImg2.height()),
                             IPL_DEPTH_8U, 1 );

    //-- Always start from zeros for now
    weightMatrix = cv::Mat::zeros(ROWS_1*ROWS_2, COLS_1*COLS_2, CV_32FC1);

    return true;
}

/************************************************************************/
void teo::ProcessorRateThread::run() {

    //-- Begin --
    iFrameGrabberImage1->getImage(inYarpImg1);
    iFrameGrabberImage2->getImage(inYarpImg2);

    cvCvtColor((IplImage*)inYarpImg1.getIplImage(), inCvImg1, CV_RGB2GRAY);
    cvCvtColor((IplImage*)inYarpImg2.getIplImage(), inCvImg2, CV_RGB2GRAY);

    cv::Mat frame1 = inCvImg1;
    cv::Mat frame2 = inCvImg2;

    //-- Process ---
    //# note the changed axis in opencv
    cv::resize(frame1, frame1_reduced, cv::Size(COLS_1, ROWS_1), cv::INTER_NEAREST);
    cv::resize(frame2, frame2_reduced, cv::Size(COLS_2, ROWS_2), cv::INTER_NEAREST);



    //-- End --
    /*yarp::sig::ImageOf<yarp::sig::PixelBgr> outYarpImg1;
    yarp::sig::ImageOf<yarp::sig::PixelBgr> outYarpImg2;
    outYarpImg1.wrapIplImage(inCvImg1);
    outYarpImg2.wrapIplImage(inCvImg1);

    ptrOutPort1->prepare() = outYarpImg1;
    ptrOutPort2->prepare() = outYarpImg2;
    ptrOutPort1->write();
    ptrOutPort2->write();*/

    return;
}

/************************************************************************/
void teo::ProcessorRateThread::threadRelease() {
    cvReleaseImage( &inCvImg1 );
    cvReleaseImage( &inCvImg2 );
    return;
}

/************************************************************************/
void teo::ProcessorRateThread::setPtrOutPort1(yarp::os::BufferedPort<yarp::sig::ImageOf<yarp::sig::PixelBgr> > *value)
{
    ptrOutPort1 = value;
}

/************************************************************************/
void teo::ProcessorRateThread::setPtrOutPort2(yarp::os::BufferedPort<yarp::sig::ImageOf<yarp::sig::PixelBgr> > *value)
{
    ptrOutPort2 = value;
}

/************************************************************************/
