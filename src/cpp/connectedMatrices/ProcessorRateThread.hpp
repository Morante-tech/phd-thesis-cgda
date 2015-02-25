// -*- mode:C++; tab-width:4; c-basic-offset:4; indent-tabs-mode:nil -*-

#ifndef __PROCESSOR_RATE_THREAD__
#define __PROCESSOR_RATE_THREAD__

#include <vector>

#include <yarp/os/RateThread.h>
#include <yarp/dev/all.h>

#include <opencv/cv.h>
#include <opencv/cvaux.h>
#include <opencv/highgui.h>

#include "ColorDebug.hpp"

#define DEFAULT_MS 50  // [ms], overwritten by parent DEFAULT_PT_MODE_MS.

#define ROWS_1 70
#define ROWS_2 70
#define alpha 0.1  //-- small alpha. at least 1/10 of beta
#define beta 1


namespace teo
{

/**
 * @ingroup teoProcessorCompensation
 *
 * The ProcessorRateThread class.
 *
 */
class ProcessorRateThread : public yarp::os::RateThread {

    public:
        // Set the Thread Rate in the class constructor
        ProcessorRateThread() : RateThread(DEFAULT_MS) {}  // In ms

        /** Initialization method. */
        virtual bool threadInit();

        /** Release method. */
        virtual void threadRelease();

        /** Loop function. This is the thread itself. */
        virtual void run();

        /** Grabber stuff */
        yarp::dev::IFrameGrabberImage * iFrameGrabberImage1;
        yarp::dev::IFrameGrabberImage * iFrameGrabberImage2;

        void setPtrOutPort1(yarp::os::BufferedPort<yarp::sig::ImageOf<yarp::sig::PixelBgr> > *value);
        void setPtrOutPort2(yarp::os::BufferedPort<yarp::sig::ImageOf<yarp::sig::PixelBgr> > *value);

protected:

        yarp::sig::ImageOf<yarp::sig::PixelRgb> inYarpImg1;
        yarp::sig::ImageOf<yarp::sig::PixelRgb> inYarpImg2;

        yarp::sig::ImageOf<yarp::sig::PixelRgb> outYarpImg1;
        yarp::sig::ImageOf<yarp::sig::PixelRgb> outYarpImg2;

        yarp::os::BufferedPort< yarp::sig::ImageOf< yarp::sig::PixelBgr > >* ptrOutPort1;
        yarp::os::BufferedPort< yarp::sig::ImageOf< yarp::sig::PixelBgr > >* ptrOutPort2;

        IplImage* inCvImg1;
        IplImage* inCvImg2;

        //--
        int COLS_1, COLS_2;
        cv::Mat weightMatrix;
        cv::Mat frame1_reduced, frame2_reduced;
        cv::Mat image_1_t_1; // # image 1 previous time
        cv::Mat image_2_t_1; // # image 2 previous time
        cv::Mat var_img1;
        cv::Mat var_img2;
        cv::Mat totalWeights;
        cv::Mat predictor_image_2;
        cv::Mat currWeightSubMatrixR2C2;
        cv::Mat elem1;
        cv::Mat elem2;
        cv::Mat elem3;
        cv::Mat elem4;
        cv::Mat elem5;
        cv::Mat newWeightSubMatrix;
        cv::Mat img1DotWeight;
        cv::Mat img1DotWeightOverTotal;
        cv::Mat adaptTypePredictor;
        cv::Mat adaptRangeWeight;
        cv::Mat adaptTypeWeight;
        cv::Mat error_image_2;

        bool loadWeightsFromFile;
        bool saveWeightsToFile;


};

}  // namespace teo

#endif  // __PROCESSOR_RATE_THREAD__

