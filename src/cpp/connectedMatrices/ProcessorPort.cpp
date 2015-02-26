// -*- mode:C++; tab-width:4; c-basic-offset:4; indent-tabs-mode:nil -*-

#include "ProcessorPort.hpp"

/************************************************************************/
bool teo::ProcessorPort::threadInit() {

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

    elem1 = cv::Mat::zeros(ROWS_2, COLS_2, CV_32FC1);
    elem2 = cv::Mat::zeros(ROWS_2, COLS_2, CV_32FC1);
    elem3 = cv::Mat::zeros(ROWS_2, COLS_2, CV_32FC1);
    elem4 = cv::Mat::zeros(ROWS_2, COLS_2, CV_32FC1);
    elem5 = cv::Mat::zeros(ROWS_2, COLS_2, CV_32FC1);
    image_1_t_1 = cv::Mat::zeros(ROWS_1, COLS_1, CV_8UC1);
    image_2_t_1 = cv::Mat::zeros(ROWS_1, COLS_1, CV_8UC1);
    var_img1 = cv::Mat::zeros(ROWS_1, COLS_1, CV_32FC1);
    var_img2 = cv::Mat::zeros(ROWS_2, COLS_2, CV_32FC1);

    currWeightSubMatrixR2C2 = cv::Mat::zeros(ROWS_2, COLS_2, CV_32FC1);
    newWeightSubMatrix = cv::Mat::zeros(ROWS_2, COLS_2, CV_32FC1);
    img1DotWeight = cv::Mat::zeros(ROWS_2, COLS_2, CV_32FC1);
    img1DotWeightOverTotal = cv::Mat::zeros(ROWS_2, COLS_2, CV_32FC1);

    adaptTypePredictor = cv::Mat::zeros(ROWS_2,COLS_2, CV_8UC1); // #first predictor map 2
    adaptRangeWeight = cv::Mat::zeros(ROWS_2,COLS_2, CV_32FC1); // #first predictor map 2
    adaptTypeWeight = cv::Mat::zeros(ROWS_2,COLS_2, CV_8UC1); // #first predictor map 2

    error_image_2 = cv::Mat::zeros(ROWS_2, COLS_2, CV_8UC1); // #first error map 2
    totalWeights = cv::Mat::zeros(ROWS_2,COLS_2, CV_32FC1);
    predictor_image_2 = cv::Mat::zeros(ROWS_2,COLS_2, CV_32FC1); // #first predictor map 2

    cv::namedWindow("WeightMatrix", cv::WINDOW_NORMAL);
    cv::namedWindow("Error 2", cv::WINDOW_NORMAL);
    cv::namedWindow("Frame 1 (Reduced, gray, then extended again)", cv::WINDOW_NORMAL);
    cv::namedWindow("Predictor 2", cv::WINDOW_NORMAL);
    cv::namedWindow("Frame 2 (Reduced, gray, then extended again)", cv::WINDOW_NORMAL);

    CD_DEBUG("\n");

    return true;
}

/************************************************************************/
void teo::ProcessorPort::run() {

    CD_DEBUG("\n");

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

    //frame reduced is equivalent to image_1_t_0 and image_2_t_0
    //# 255.0 forcing float type
    cv::absdiff(frame1_reduced, image_1_t_1, var_img1);
    var_img1.convertTo(var_img1, CV_32FC1);
    var_img1 = var_img1 / 255.0;


    cv::absdiff(frame2_reduced, image_2_t_1, var_img2);
    var_img2.convertTo(var_img2, CV_32FC1);
    var_img2 = var_img2 / 255.0;

    predictor_image_2 = cv::Mat::zeros(predictor_image_2.rows, predictor_image_2.cols, CV_32FC1); // #first predictor map 2
    totalWeights = cv::Mat::zeros(totalWeights.rows, totalWeights.cols, CV_32FC1); // #first predictor map 2

    for(int i=0; i < ROWS_1; i++){
        for(int j=0; j < COLS_1; j++){

            //be careful, it may be not copying, but linking when not using clone. clone could be slow
            weightMatrix( cv::Rect(cv::Point(j*COLS_2,i*ROWS_2), cv::Point(j*COLS_2+COLS_2,i*ROWS_2+ROWS_2))).copyTo(currWeightSubMatrixR2C2);
            //currWeightSubMatrixR2C2 = weightMatrix( Rect(Point(j*COLS_2,i*ROWS_2), Point(j*COLS_2+COLS_2,i*ROWS_2+ROWS_2)) ).clone();

            //   cout << currWeightSubMatrixR2C2 << endl;

            if(loadWeightsFromFile == false){
                //#the elements that add value to the weights
                elem1  = alpha * var_img1.at<float>(i,j) * var_img2;
                cv::add(currWeightSubMatrixR2C2, elem1, elem2);

                //#the elements that subtract value to the weights
                cv::absdiff(var_img1.at<float>(i,j), var_img2, elem3);

                elem4 = beta * elem3;

                //#Subtraction of both elems
                elem5 = elem2-elem4;

                //# limiting weights between 0 and 1
                cv::threshold( elem5, newWeightSubMatrix, 1, 1, cv::THRESH_TRUNC );
                cv::threshold( newWeightSubMatrix, newWeightSubMatrix, 0, 0, cv::THRESH_TOZERO );

                //#assign new weight to cell in DB
                // maybe its not neccesarry in c++, direct asignation
                //copy or clone?

                newWeightSubMatrix.copyTo(weightMatrix(cv::Rect(cv::Point(j*COLS_2,i*ROWS_2), cv::Point(j*COLS_2+COLS_2,i*ROWS_2+ROWS_2)) ));

                cv::add(totalWeights, newWeightSubMatrix, totalWeights);

            } //if
            else{
                cv::add(totalWeights, newWeightSubMatrix, totalWeights);
            }//else

        }//for j
    } //for i


    for(int i=0; i < ROWS_1; i++){
        for(int j=0; j < COLS_1; j++){
            //copy or clone?
            weightMatrix(cv::Rect(cv::Point(j*COLS_2,i*ROWS_2), cv::Point(j*COLS_2+COLS_2,i*ROWS_2+ROWS_2))).copyTo(currWeightSubMatrixR2C2);

            img1DotWeight = frame1_reduced.at<uchar>(i,j)*currWeightSubMatrixR2C2;

            img1DotWeightOverTotal = img1DotWeight / totalWeights;

            cv::add(predictor_image_2, img1DotWeightOverTotal, predictor_image_2);

            cv::threshold( predictor_image_2, predictor_image_2, 255, 255, cv::THRESH_TRUNC);
            cv::threshold( predictor_image_2, predictor_image_2, 0, 255, cv::THRESH_TOZERO );

        }//for j
    }//for i

    //#update previous image
    frame1_reduced.copyTo(image_1_t_1);
    frame2_reduced.copyTo(image_2_t_1);

    //-- End (visualization) --

    cvWaitKey(1);

    //     #### PREDICTOR MAPS ######
    predictor_image_2.convertTo(adaptTypePredictor, CV_8UC1);
    cv::imshow("Predictor 2", adaptTypePredictor);
    //j//IplImage outCvImg1 = adaptTypePredictor;
    //j//outYarpImg1.wrapIplImage( &outCvImg1 );

    //    #### SHOW ORIGINAL IMAGES ######
    cv::imshow("Frame 1 (Reduced, gray, then extended again)", frame1_reduced);
    //j//IplImage outCvImg2 = frame1_reduced;
    //j//outYarpImg2.wrapIplImage( &outCvImg2 );
    cv::imshow("Frame 2 (Reduced, gray, then extended again)", frame2_reduced);
    //j//IplImage outCvImg3 = frame2_reduced;
    //j//outYarpImg3.wrapIplImage( &outCvImg3 );

    //    #### WEIGHT MAPS ####
    adaptRangeWeight = 255* weightMatrix.clone();
    adaptRangeWeight.convertTo(adaptTypeWeight, CV_8UC1);
    cv::imshow("WeightMatrix",adaptTypeWeight);
    //j//IplImage outCvImg4 = adaptTypeWeight;
    //j//outYarpImg4.wrapIplImage( &outCvImg4 );

    // #### ERROR MAPS ######
    cv::absdiff(adaptTypePredictor, frame2_reduced, error_image_2);
    cv::imshow("Error 2", error_image_2);
    //j//IplImage outCvImg5 = error_image_2;
    //j//outYarpImg5.wrapIplImage( &outCvImg5 );


    /*ptrOutPort1->prepare() = outYarpImg1;
    ptrOutPort2->prepare() = outYarpImg2;
    ptrOutPort3->prepare() = outYarpImg3;
    ptrOutPort4->prepare() = outYarpImg4;
    ptrOutPort5->prepare() = outYarpImg5;
    ptrOutPort1->write();
    ptrOutPort2->write();
    ptrOutPort3->write();
    ptrOutPort4->write();
    ptrOutPort5->write();*/

    return;
}

/************************************************************************/
void teo::ProcessorPort::threadRelease() {
    cvReleaseImage( &inCvImg1 );
    cvReleaseImage( &inCvImg2 );
    return;
}

/************************************************************************/
void teo::ProcessorPort::setPtrOutPort1(yarp::os::BufferedPort<yarp::sig::ImageOf<yarp::sig::PixelMono> > *value)
{
    ptrOutPort1 = value;
}

/************************************************************************/
void teo::ProcessorPort::setPtrOutPort2(yarp::os::BufferedPort<yarp::sig::ImageOf<yarp::sig::PixelMono> > *value)
{
    ptrOutPort2 = value;
}

/************************************************************************/
void teo::ProcessorPort::setPtrOutPort3(yarp::os::BufferedPort<yarp::sig::ImageOf<yarp::sig::PixelMono> > *value)
{
    ptrOutPort3 = value;
}

/************************************************************************/
void teo::ProcessorPort::setPtrOutPort4(yarp::os::BufferedPort<yarp::sig::ImageOf<yarp::sig::PixelMono> > *value)
{
    ptrOutPort4 = value;
}

/************************************************************************/
void teo::ProcessorPort::setPtrOutPort5(yarp::os::BufferedPort<yarp::sig::ImageOf<yarp::sig::PixelMono> > *value)
{
    ptrOutPort5 = value;
}

/************************************************************************/
