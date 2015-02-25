#include <iostream>
//#include <opencv2/opencv.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <opencv2/core/core.hpp>
#include <opencv2/imgproc/imgproc.hpp>
//#include <yarp/math/Math.h>
#include <sstream>
#include <string>


using namespace std;
using namespace cv;

int main(){

    //tatup video
    VideoCapture cap1("../../../../feed/videos/tatup.mp4"); // open the video file for reading
    VideoCapture cap2("../../../../feed/videos/tatup.mp4"); // open the video file for reading

    //synthetic video
    //    VideoCapture cap1("../../../..feed/videos/synthetic2.ogg"); // open the video file for reading
    //    VideoCapture cap2("../../../..feed/videos/synthetic2.ogg"); // open the video file for reading


    //    VideoCapture cap1(0); // open the video file for reading
    //    VideoCapture cap2(2); // open the video file for reading

    //cap1.set(CV_CAP_PROP_FPS,15);
    cap2.set(CV_CAP_PROP_FPS,15);

    if (!cap1.isOpened() || !cap2.isOpened()){
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
    int ROWS_1 = 10;
    int COLS_1 = ROWS_1 * frame1Cols / frame1Rows;
    int ROWS_2 = 10;
    int COLS_2 = ROWS_2 * frame2Cols / frame2Rows;
    float alpha = 0.1; // small alpha. at least 1/10 of beta
    float beta = 1;
    int msToWait= 1;
    bool loadWeightsFromFile = false;
    bool saveWeightsToFile   = false;
// ###############
    std::stringstream ss1, ss2;
    ss1 << ROWS_1;
    ss2 << ROWS_2;
    string weightsFilename = "data/weightMatrix" + ss1.str() + "-" + ss2.str(); // + ".npy";
    //############################

    //###############################
    Mat weightMatrix;
    if(loadWeightsFromFile == true){
        weightMatrix = imread(weightsFilename, CV_32FC1);
    }
    else{
        weightMatrix = Mat::zeros(ROWS_1*ROWS_2, COLS_1*COLS_2, CV_32FC1);
    }


    // some neccesary initialization
    Mat image_1_t_1  =  Mat::zeros(ROWS_1, COLS_1, CV_8UC1); // # image 1 previous time
    Mat image_2_t_1  =  Mat::zeros(ROWS_2, COLS_2, CV_8UC1); // # image 2 previous time

    Mat image_1_t_0  =  Mat::zeros(ROWS_1, COLS_1, CV_8UC1);
    Mat image_2_t_0  =  Mat::zeros(ROWS_2, COLS_2, CV_8UC1);

    Mat error_image_2 = Mat::zeros(ROWS_2, COLS_2, CV_8UC1); // #first error map 2

    Mat totalWeights = Mat::zeros(ROWS_2,COLS_2, CV_32FC1);
    Mat predictor_image_2 = Mat::zeros(ROWS_2,COLS_2, CV_32FC1); // #first predictor map 2

    Mat var_img1  =  Mat::zeros(ROWS_1, COLS_1, CV_32FC1);
    Mat var_img2  =  Mat::zeros(ROWS_2, COLS_2, CV_32FC1);

    Mat frame1_reduced, frame2_reduced;
    Mat elem1(Mat::zeros(ROWS_2, COLS_2, CV_32FC1));
    Mat elem2(Mat::zeros(ROWS_2, COLS_2, CV_32FC1));
    Mat elem3(Mat::zeros(ROWS_2, COLS_2, CV_32FC1));
    Mat elem4(Mat::zeros(ROWS_2, COLS_2, CV_32FC1));
    Mat elem5(Mat::zeros(ROWS_2, COLS_2, CV_32FC1));

    Mat currWeightSubMatrixR2C2(Mat::zeros(ROWS_2, COLS_2, CV_32FC1));
    Mat newWeightSubMatrix(Mat::zeros(ROWS_2, COLS_2, CV_32FC1));
    Mat img1DotWeight(Mat::zeros(ROWS_2, COLS_2, CV_32FC1));
    Mat img1DotWeightOverTotal(Mat::zeros(ROWS_2, COLS_2, CV_32FC1));
    Mat temp_pred_2 = Mat::zeros(ROWS_2,COLS_2, CV_32FC1);
    Mat adaptTypePredictor = Mat::zeros(ROWS_2,COLS_2, CV_8UC1); // #first predictor map 2
    Mat adaptRangeWeight = Mat::zeros(ROWS_2,COLS_2, CV_32FC1); // #first predictor map 2
    Mat adaptTypeWeight = Mat::zeros(ROWS_2,COLS_2, CV_8UC1); // #first predictor map 2

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
        divide(var_img1, 255, var_img1);

        //error aqui
        cout << var_img1<< endl;

        cv::absdiff(image_2_t_0, image_2_t_1, var_img2);
        divide(var_img2, 255.0, var_img2);

        predictor_image_2 = cv::Mat::zeros(predictor_image_2.rows, predictor_image_2.cols, CV_32FC1); // #first predictor map 2
        totalWeights = cv::Mat::zeros(totalWeights.rows, totalWeights.cols, CV_32FC1); // #first predictor map 2

        for(int i=0; i < ROWS_1; i++){
            for(int j=0; j < COLS_1; j++){

                //be careful, it may be not copying, but linking when not using clone. clone could be slow
                currWeightSubMatrixR2C2 = weightMatrix( Rect(Point(j*COLS_2,i*ROWS_2), Point(j*COLS_2+COLS_2,i*ROWS_2+ROWS_2)) ).clone();

                if(loadWeightsFromFile == false){
                    //#the elements that add value to the weights
                    elem1  = (alpha * var_img1.at<float>(i,j) * var_img2, CV_32FC1);

                  //  cout << var_img1.at<float>(i,j) << endl;

                    cv::add(currWeightSubMatrixR2C2, elem1, elem2);

                    //#the elements that subtract value to the weights
                    absdiff(var_img1.at<float>(i,j), var_img2, elem3);
                    multiply(elem3, beta, elem4);


                    //#Subtraction of both elems
                    elem5 = (elem2-elem4, CV_32FC1);


                    //# limiting weights between 0 and 1
                    threshold( elem5, newWeightSubMatrix, 1, 1, cv::THRESH_TRUNC );
                    threshold( newWeightSubMatrix, newWeightSubMatrix, 0, 0, THRESH_TOZERO );

                    //#assign new weight to cell in DB
                    // maybe its not neccesarry in c++, direct asignation
                    //copy or clone?
                    currWeightSubMatrixR2C2.copyTo(weightMatrix( Rect(Point(j*COLS_2,i*ROWS_2), Point(j*COLS_2+COLS_2,i*ROWS_2+ROWS_2)) ));
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
                currWeightSubMatrixR2C2 = weightMatrix( Rect(Point(j*COLS_2,i*ROWS_2), Point(j*COLS_2+COLS_2,i*ROWS_2+ROWS_2)) ).clone();
                img1DotWeight = (image_1_t_0.at<uchar>(i,j)*currWeightSubMatrixR2C2);
                img1DotWeightOverTotal = img1DotWeight / totalWeights;
                cv::add(predictor_image_2, img1DotWeightOverTotal, temp_pred_2);
                threshold( predictor_image_2, predictor_image_2, 255, 255, cv::THRESH_TRUNC );
                threshold( predictor_image_2, predictor_image_2, 0, 0, THRESH_TOZERO );
            }//for j
        }//for i

        //#update previous image
        image_1_t_1 = image_1_t_0.clone();
        image_2_t_1 = image_2_t_0.clone();


        //    ###########################################
        //    ########### VISUALIZATION #################
        //    ###########################################

        //     #### PREDICTOR MAPS ######
        predictor_image_2.convertTo(adaptTypePredictor, CV_8UC1);
        namedWindow("Predictor 2", WINDOW_NORMAL);
        imshow("Predictor 2", adaptTypePredictor);

        //    #### SHOW ORIGINAL IMAGES ######
        namedWindow("Frame 1 (Reduced, gray, then extended again)", WINDOW_NORMAL);
        imshow("Frame 1 (Reduced, gray, then extended again)", image_1_t_0);

        namedWindow("Frame 2 (Reduced, gray, then extended again)", WINDOW_NORMAL);
        imshow("Frame 2 (Reduced, gray, then extended again)", image_2_t_0);

        //    #### WEIGHT MAPS ####
        adaptRangeWeight = 255* weightMatrix.clone();
        adaptRangeWeight.convertTo(adaptTypeWeight, CV_8UC1);
        namedWindow("WeightMatrix", WINDOW_NORMAL);
        imshow("WeightMatrix",adaptTypeWeight);


       // #### ERROR MAPS ######
        absdiff(adaptTypePredictor, image_2_t_0, error_image_2);
        namedWindow("Error 2", WINDOW_NORMAL);
        imshow("Error 2", error_image_2);

        // escape key, not q as in python
        if (cv::waitKey(msToWait) == 27 ){
            if(saveWeightsToFile == true){
                imwrite(weightsFilename,weightMatrix);
            }//if
            break;
        }//if

    } //while


    //    #########################################################
    //    #####################   END LOOP   #####################

    destroyAllWindows();

    return 0;
}

