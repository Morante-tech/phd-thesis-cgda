#include <iostream>
//#include <opencv2/opencv.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <opencv2/core/core.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include <yarp/math/Math.h>
#include <sstream>
#include <string>


using namespace std;
using namespace cv;

int main()
{
    //tatup video
    VideoCapture cap1("/home/smorante/Repositories/connected-images/feed/videos/tatup.mp4"); // open the video file for reading
    VideoCapture cap2("/home/smorante/Repositories/connected-images/feed/videos/tatup.mp4"); // open the video file for reading

    //synthetic video
    //    VideoCapture cap1('feed/videos/synthetic2.ogg'); // open the video file for reading
    //    VideoCapture cap2('feed/videos/synthetic2.ogg'); // open the video file for reading


    //    VideoCapture cap1(0); // open the video file for reading
    //    VideoCapture cap2(2); // open the video file for reading

    cap1.set(CV_CAP_PROP_FPS,15);
    cap2.set(CV_CAP_PROP_FPS,15);

    if (!cap1.isOpened() || !cap2.isOpened())  // if not success, exit program
    {
        cout << "Cannot extract images from video" << endl;
        return -1;
    }
    Mat frame1, frame2;
    bool ret1 = cap1.read(frame1); // read a new frame from video
    bool ret2 = cap2.read(frame2); // read a new frame from video
    int frame1Rows = frame1.rows;
    int frame1Cols = frame1.cols;
    int frame2Rows = frame2.rows;
    int frame2Cols = frame2.cols;

    //##### PARAMETERS ###########
    int ROWS_1 = 4;
    int COLS_1 = ROWS_1 * frame1Cols / frame1Rows;
    int ROWS_2 = 4;
    int COLS_2 = ROWS_2 * frame2Cols / frame2Rows;
    float alpha = 0.1; // small alpha. at least 1/10 of beta
    float beta = 1;
    int msToWait= 1;
    bool loadWeightsFromFile = false;
    bool saveWeightsToFile   = false;

    std::stringstream ss1, ss2;
    ss1 << ROWS_1;
    ss2 << ROWS_2;

    //std::string str1= ss1.str();
    //std::string str2= ss2.str(ROWS_2);
    string weightsFilename = "data/weightMatrix" + ss1.str() + "-" + ss2.str(); // + ".npy";
    //############################

    //###############################
    Mat weightMatrix;
    if(loadWeightsFromFile == true){
        weightMatrix = imread(weightsFilename, CV_LOAD_IMAGE_ANYDEPTH);
    }
    else{
        weightMatrix = Mat::zeros(ROWS_1*ROWS_2, COLS_1*COLS_2, CV_LOAD_IMAGE_ANYDEPTH);
    }


    // some neccesary initialization
    Mat image_1_t_1  =  Mat::zeros(ROWS_1, COLS_1, CV_LOAD_IMAGE_GRAYSCALE); // # image 1 previous time
    Mat image_2_t_1  =  Mat::zeros(ROWS_2, COLS_2, CV_LOAD_IMAGE_GRAYSCALE); // # image 2 previous time

    Mat image_1_t_0  =  Mat::zeros(ROWS_1, COLS_1, CV_LOAD_IMAGE_GRAYSCALE); // # image 1 previous time
    Mat image_2_t_0  =  Mat::zeros(ROWS_2, COLS_2, CV_LOAD_IMAGE_GRAYSCALE); // # image 2 previous time

    Mat error_image_2 = Mat::zeros(ROWS_2, COLS_2, CV_LOAD_IMAGE_GRAYSCALE); // #first error map 2
    Mat totalWeights = Mat::zeros(ROWS_2,COLS_2, CV_LOAD_IMAGE_ANYDEPTH);
    Mat predictor_image_2 = Mat::zeros(ROWS_2,COLS_2, CV_LOAD_IMAGE_ANYDEPTH); // #first predictor map 2

    Mat var_img1  =  Mat::zeros(ROWS_1, COLS_1, CV_LOAD_IMAGE_ANYDEPTH); // # image 1 previous time
    Mat var_img2  =  Mat::zeros(ROWS_2, COLS_2, CV_LOAD_IMAGE_ANYDEPTH); // # image 2 previous time

    Mat frame1_reduced, frame2_reduced;
    Mat currWeightSubMatrixR2C2;
    Mat elem1(Mat::zeros(ROWS_2, COLS_2, CV_LOAD_IMAGE_ANYDEPTH));
    Mat elem2(Mat::zeros(ROWS_2, COLS_2, CV_LOAD_IMAGE_ANYDEPTH));
    Mat elem3(Mat::zeros(ROWS_2, COLS_2, CV_LOAD_IMAGE_ANYDEPTH));
    Mat elem4(Mat::zeros(ROWS_2, COLS_2, CV_LOAD_IMAGE_ANYDEPTH));
    Mat elem5(Mat::zeros(ROWS_2, COLS_2, CV_LOAD_IMAGE_ANYDEPTH));

    //###############################
    //############ LOOP #############
    while(cap1.isOpened() && cap2.isOpened()){

        ret1 = cap1.read(frame1); // read a new frame from video
        ret2 = cap2.read(frame2); // read a new frame from video

        if(ret1 == false || ret2 == false){
            cout << "No stream of images!!" << endl;
            break;
        }

        //# note the changed axis in opencv
        cv::resize(frame1, frame1_reduced, Size(COLS_1, ROWS_1), INTER_NEAREST);
        cv::resize(frame2, frame2_reduced, Size(COLS_2, ROWS_2), INTER_NEAREST);

        cv::cvtColor(frame1_reduced, image_1_t_0, COLOR_BGR2GRAY);
        cv::cvtColor(frame2_reduced, image_2_t_0, COLOR_BGR2GRAY);

        //# 255.0 forcing float type
        cv::absdiff(image_1_t_0, image_1_t_1, var_img1);
        var_img1 = var_img1/255.0;

        cv::absdiff(image_2_t_0, image_2_t_1, var_img2);
        var_img2 = var_img2/255.0;

        predictor_image_2 = cv::Mat::zeros(predictor_image_2.rows, predictor_image_2.cols, CV_LOAD_IMAGE_ANYDEPTH); // #first predictor map 2
        totalWeights = cv::Mat::zeros(totalWeights.rows, totalWeights.cols, CV_LOAD_IMAGE_ANYDEPTH); // #first predictor map 2

        for(int i=0; i < ROWS_1; i++){
            for(int j=0; j < COLS_1; j++){

                currWeightSubMatrixR2C2 = Mat(weightMatrix, Rect(Point(j*COLS_2,i*ROWS_2), Point(j*COLS_2+COLS_2,i*ROWS_2+ROWS_2) ) );


                if(loadWeightsFromFile == false){
                    //#the elements that add value to the weights
                    elem1  = alpha * var_img1.at<uchar>(i,j) * var_img2;
              //      cv::add(currWeightSubMatrixR2C2, elem1, elem2);

                    //#the elements that subtract value to the weights
                //    absdiff(var_img1.at<uchar>(i,j), var_img2, elem3);
                  //  elem4 = elem3 * beta;

                    //#Subtraction of both elems
                   // elem5 = elem2-elem4;
                   // cout << elem5 << endl;
                   // cout << "here" << endl;

                } //if


            }// for j
        } // for i


    } //while

    return 0;
}

