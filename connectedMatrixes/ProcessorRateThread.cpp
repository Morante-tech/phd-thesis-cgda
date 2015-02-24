// -*- mode:C++; tab-width:4; c-basic-offset:4; indent-tabs-mode:nil -*-

#include "ProcessorRateThread.hpp"

/************************************************************************/
bool teo::ProcessorRateThread::threadInit() {

    return true;
}

/************************************************************************/
void teo::ProcessorRateThread::run() {

    //-- Begin --
    iFrameGrabberImage1->getImage(inYarpImg1);
    iFrameGrabberImage1->getImage(inYarpImg2);
    printf("iFrameGrabberImage1 got a %dx%d image\n", inYarpImg1.width(), inYarpImg1.height());
    printf("iFrameGrabberImage2 got a %dx%d image\n", inYarpImg2.width(), inYarpImg2.height());

    IplImage *inCvImg1 = cvCreateImage(cvSize(inYarpImg1.width(),
                                              inYarpImg1.height()),
                                              IPL_DEPTH_8U, 3 );
    cvCvtColor((IplImage*)inYarpImg1.getIplImage(), inCvImg1, CV_RGB2BGR);

    //-- Process ---



    //-- End --
    yarp::sig::ImageOf<yarp::sig::PixelBgr> outYarpImg1;
    yarp::sig::ImageOf<yarp::sig::PixelBgr> outYarpImg2;
    outYarpImg1.wrapIplImage(inCvImg1);
    outYarpImg2.wrapIplImage(inCvImg1);

    ptrOutPort1->prepare() = outYarpImg1;
    ptrOutPort2->prepare() = outYarpImg2;
    ptrOutPort1->write();
    ptrOutPort2->write();

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
