/*
Author: Santiago Morante
Robotics Lab. Universidad Carlos III de Madrid

About: This file (when finished) captures two videos, and trains weights
to relate both images. After training (in fact, it is online, so I should say
'when enough time has passed') it can predict movements between cameras.
*/

#include <iostream>
#include <sstream>
#include <string>
#include <stdio.h>

#include <opencv2/highgui/highgui.hpp>
#include <opencv2/core/core.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include <opencv2/gpu/gpu.hpp>


int main(){

    //read video
    cv::gpu::VideoReader_GPU cap1("../../../../feed/videos/tatup.mp4");
    cv::gpu::VideoReader_GPU cap2("../../../../feed/videos/tatup.mp4");

    if (!cap1.isOpened() || !cap2.isOpened()){
        std::cout << "Cannot extract images from video" << std::endl;
        return -1;
    }
    cv::gpu::GpuMat frame1, frame2;

    bool ret1 = cap1.read(frame1); // read a new frame from video
    bool ret2 = cap2.read(frame2); // read a new frame from video
    int frame1Rows = frame1.rows;
    int frame1Cols = frame1.cols;
    int frame2Rows = frame2.rows;
    int frame2Cols = frame2.cols;

    //##### PARAMETERS ###########
    int ROWS_1 = 70;
    int COLS_1 = ROWS_1 * frame1Cols / frame1Rows;
    int ROWS_2 = 70;
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
    std::string weightsFilename = "data/weightMatrix" + ss1.str() + "-" + ss2.str(); // + ".npy";
    //############################

    //###############################
    cv::Mat weightMatrix_cpu;
    cv::gpu::GpuMat weightMatrix;

    if(loadWeightsFromFile == true){
        weightMatrix_cpu = cv::imread(weightsFilename, CV_32FC1);
        weightMatrix.upload(weightMatrix_cpu);

    }
    else{
        weightMatrix_cpu = cv::Mat::zeros(ROWS_1*ROWS_2, COLS_1*COLS_2, CV_32FC1);
        weightMatrix.upload(weightMatrix_cpu);

    }


    // some neccesary initialization
    cv::gpu::GpuMat image_1_t_1 (ROWS_1, COLS_1, CV_8UC1); // # image 1 previous time
    image_1_t_1.setTo(cv::Scalar::all(0));

    cv::gpu::GpuMat image_2_t_1(ROWS_2, COLS_2, CV_8UC1); // # image 2 previous time
    image_2_t_1.setTo(cv::Scalar::all(0));

    cv::gpu::GpuMat image_1_t_0(ROWS_1, COLS_1, CV_8UC1);
    image_1_t_0.setTo(cv::Scalar::all(0));

    cv::gpu::GpuMat image_2_t_0(ROWS_2, COLS_2, CV_8UC1);
    image_2_t_0.setTo(cv::Scalar::all(0));

    cv::gpu::GpuMat error_image_2(ROWS_2, COLS_2, CV_8UC1); // #first error map 2
    error_image_2.setTo(cv::Scalar::all(0));

    cv::gpu::GpuMat totalWeights(ROWS_2,COLS_2, CV_32FC1);
    totalWeights.setTo(cv::Scalar::all(0));

    cv::gpu::GpuMat predictor_image_2(ROWS_2,COLS_2, CV_32FC1); // #first predictor map 2
    predictor_image_2.setTo(cv::Scalar::all(0));

    cv::gpu::GpuMat var_img1(ROWS_1, COLS_1, CV_32FC1);
    var_img1.setTo(cv::Scalar::all(0));

    cv::gpu::GpuMat var_img2 (ROWS_2, COLS_2, CV_32FC1);
    var_img2.setTo(cv::Scalar::all(0));

    cv::gpu::GpuMat frame1_reduced, frame2_reduced;
    cv::gpu::GpuMat elem1(ROWS_2, COLS_2, CV_32FC1);
    elem1.setTo(cv::Scalar::all(0));

    cv::gpu::GpuMat elem2(ROWS_2, COLS_2, CV_32FC1);
    elem2.setTo(cv::Scalar::all(0));

    cv::gpu::GpuMat elem3(ROWS_2, COLS_2, CV_32FC1);
    elem3.setTo(cv::Scalar::all(0));

    cv::gpu::GpuMat elem4(ROWS_2, COLS_2, CV_32FC1);
    elem4.setTo(cv::Scalar::all(0));

    cv::gpu::GpuMat elem5(ROWS_2, COLS_2, CV_32FC1);
    elem5.setTo(cv::Scalar::all(0));

    cv::gpu::GpuMat currWeightSubMatrixR2C2(ROWS_2, COLS_2, CV_32FC1);
    currWeightSubMatrixR2C2.setTo(cv::Scalar::all(0));

    cv::gpu::GpuMat newWeightSubMatrix(ROWS_2, COLS_2, CV_32FC1);
    newWeightSubMatrix.setTo(cv::Scalar::all(0));

    cv::gpu::GpuMat img1DotWeight(ROWS_2, COLS_2, CV_32FC1);
    img1DotWeight.setTo(cv::Scalar::all(0));

    cv::gpu::GpuMat img1DotWeightOverTotal(ROWS_2, COLS_2, CV_32FC1);
    img1DotWeightOverTotal.setTo(cv::Scalar::all(0));

    cv::gpu::GpuMat adaptTypePredictor(ROWS_2,COLS_2, CV_8UC1);
    adaptTypePredictor.setTo(cv::Scalar::all(0));

    cv::gpu::GpuMat adaptRangeWeight (ROWS_2,COLS_2, CV_32FC1);
    adaptRangeWeight.setTo(cv::Scalar::all(0));

    cv::gpu::GpuMat adaptTypeWeight (ROWS_2,COLS_2, CV_8UC1);
    adaptTypeWeight.setTo(cv::Scalar::all(0));


    //###############################
    //############ LOOP #############
    while(cap1.isOpened() && cap2.isOpened()){

        ret1 = cap1.read(frame1); // read a new frame from video
        ret2 = cap2.read(frame2); // read a new frame from video

        if(ret1 == false || ret2 == false){
            std::cout << "No stream of images!!" << std::endl;
            break;
        }

        //# note the changed axis in opencv
        cv::gpu::resize(frame1, frame1_reduced, cv::Size(COLS_1, ROWS_1), cv::INTER_NEAREST);
        cv::gpu::resize(frame2, frame2_reduced, cv::Size(COLS_2, ROWS_2), cv::INTER_NEAREST);

        cv::gpu::cvtColor(frame1_reduced, image_1_t_0, cv::COLOR_BGR2GRAY);
        cv::gpu::cvtColor(frame2_reduced, image_2_t_0, cv::COLOR_BGR2GRAY);

        //# 255.0 forcing float type
        cv::gpu::absdiff(image_1_t_0, image_1_t_1, var_img1);
        var_img1.convertTo(var_img1, CV_32FC1);
        var_img1 = var_img1 / 255.0;


        cv::gpu::absdiff(image_2_t_0, image_2_t_1, var_img2);
        var_img2.convertTo(var_img2, CV_32FC1);
        var_img2 = var_img2 / 255.0;


        predictor_image_2.setTo(cv::Scalar::all(0));
        totalWeights.setTo(cv::Scalar::all(0));

        for(int i=0; i < ROWS_1; i++){
            for(int j=0; j < COLS_1; j++){

                //be careful, it may be not copying, but linking when not using clone. clone could be slow
                weightMatrix( Rect(Point(j*COLS_2,i*ROWS_2), Point(j*COLS_2+COLS_2,i*ROWS_2+ROWS_2))).copyTo(currWeightSubMatrixR2C2);
                //currWeightSubMatrixR2C2 = weightMatrix( Rect(Point(j*COLS_2,i*ROWS_2), Point(j*COLS_2+COLS_2,i*ROWS_2+ROWS_2)) ).clone();

             //   cout << currWeightSubMatrixR2C2 << endl;

                if(loadWeightsFromFile == false){
                    //#the elements that add value to the weights
                    elem1  = alpha * var_img1.at<float>(i,j) * var_img2;
                    cv::gpu::add(currWeightSubMatrixR2C2, elem1, elem2);

                    //#the elements that subtract value to the weights
                    cv::gpu::absdiff(var_img1.at<float>(i,j), var_img2, elem3);

                    elem4 = beta * elem3;

                    //#Subtraction of both elems
                    elem5 = elem2-elem4;

                    //# limiting weights between 0 and 1
                    cv::gpu::threshold( elem5, newWeightSubMatrix, 1, 1, cv::THRESH_TRUNC );
                    cv::gpu::threshold( newWeightSubMatrix, newWeightSubMatrix, 0, 0, cv::THRESH_TOZERO );

                    //#assign new weight to cell in DB
                    // maybe its not neccesarry in c++, direct asignation
                    //copy or clone?

                    newWeightSubMatrix.copyTo(weightMatrix( Rect(Point(j*COLS_2,i*ROWS_2), Point(j*COLS_2+COLS_2,i*ROWS_2+ROWS_2)) ));

                    cv::gpu::add(totalWeights, newWeightSubMatrix, totalWeights);

                } //if
                else{
                    cv::gpu::add(totalWeights, newWeightSubMatrix, totalWeights);
                }//else

            }//for j
        } //for i

        for(int i=0; i < ROWS_1; i++){
            for(int j=0; j < COLS_1; j++){
                //copy or clone?
                weightMatrix( Rect(Point(j*COLS_2,i*ROWS_2), Point(j*COLS_2+COLS_2,i*ROWS_2+ROWS_2))).copyTo(currWeightSubMatrixR2C2);


                img1DotWeight = image_1_t_0.at<uchar>(i,j)*currWeightSubMatrixR2C2;

                img1DotWeightOverTotal = img1DotWeight / totalWeights;

                cv::gpu::add(predictor_image_2, img1DotWeightOverTotal, predictor_image_2);

                cv::gpu::threshold( predictor_image_2, predictor_image_2, 255, 255, cv::THRESH_TRUNC);
                cv::gpu::threshold( predictor_image_2, predictor_image_2, 0, 255, cv::THRESH_TOZERO );


            }//for j
        }//for i

        //#update previous image
        image_1_t_0.copyTo(image_1_t_1);
        image_2_t_0.copyTo(image_2_t_1);

        //    ###########################################
        //    ########### VISUALIZATION #################
        //    ###########################################

        //     #### PREDICTOR MAPS ######
        predictor_image_2.convertTo(adaptTypePredictor, CV_8UC1);
        cv::namedWindow("Predictor 2", cv::WINDOW_OPENGL);
        cv::imshow("Predictor 2", adaptTypePredictor);

        //    #### SHOW ORIGINAL IMAGES ######
        cv::namedWindow("Frame 1 (Reduced, gray, then extended again)", cv::WINDOW_OPENGL);
        cv::imshow("Frame 1 (Reduced, gray, then extended again)", image_1_t_0);

        cv::namedWindow("Frame 2 (Reduced, gray, then extended again)", cv::WINDOW_OPENGL);
        cv::imshow("Frame 2 (Reduced, gray, then extended again)", image_2_t_0);

        //    #### WEIGHT MAPS ####
//        adaptRangeWeight = 255* weightMatrix.clone();
//        adaptRangeWeight.convertTo(adaptTypeWeight, CV_8UC1);
//        cv::namedWindow("WeightMatrix", cv::WINDOW_OPENGL);
//        cv::imshow("WeightMatrix",adaptTypeWeight);


       // #### ERROR MAPS ######
        cv::gpu::absdiff(adaptTypePredictor, image_2_t_0, error_image_2);
        cv::namedWindow("Error 2", cv::WINDOW_OPENGL);
        cv::imshow("Error 2", error_image_2);

        // escape key, not q as in python
        if (cv::waitKey(msToWait) == 27 ){
            if(saveWeightsToFile == true){
                cv::imwrite(weightsFilename, weightMatrix);
            }//if
            break;
        }//if

    } //while


    //    #########################################################
    //    #####################   END LOOP   #####################

    destroyAllWindows();

    return 0;
}

