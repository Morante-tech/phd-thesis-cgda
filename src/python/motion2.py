# -*- coding: utf-8 -*-
"""
Author: Santiago Morante
Robotics Lab. Universidad Carlos III de Madrid
About: This file (when finished) captures two videos, and trains weights
to relate both images. After training (in fact, it is online, so I should say
'when enough time has elapsed') it can predict movements between cameras.
"""

import numpy as np
import libmotion
import cv2
import time
import csv
import sys
import os
############################

def extract_params_from_file(filename):
    #### REPRODUCE EXPERIMENT ####
    experiment_list=[]
    with open(filename, "rb") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            experiment_list.append(row)
    print "[INFO] Experiment raw data: ", experiment_list [1]
    
    input_matrix = experiment_list [1][0]
    output_matrix = experiment_list [1][1]
    filename_precomputed_weights = experiment_list [1][2]
    input_rows = int(experiment_list [1][5])
    input_cols = int(experiment_list [1][6])
    output_rows = int(experiment_list [1][7])
    output_cols = int(experiment_list [1][8])
    alpha_param = float(experiment_list [1][9])
    lambda_param = float(experiment_list [1][10])
    if experiment_list [1][11] == "True":
        actual_images = True
    elif(experiment_list [1][11] == "False"):
        actual_images = False
    else:
        raise NameError("[ERROR] Undefined ACTUAL_IMAGES from file")    

    interpolation_type = int(experiment_list [1][12])
    
    return (input_matrix, output_matrix, filename_precomputed_weights,
    input_rows, input_cols, output_rows, output_cols, alpha_param, lambda_param,
    actual_images, interpolation_type)

############################

REPRODUCE_EXPERIMENT = False    
EXPERIMENT_PARAMS_FILENAME = ""
SAVE_EXPERIMENT   = False
EXTERNAL_WEIGHTS = False
FILENAME_PRECOMPUTED_WEIGHTS = ""

#### REPRODUCING EXPERIMENT ####
if len(sys.argv) > 2:
    sys.exit("Usage: script.py params_file.csv")
    
elif len(sys.argv) == 2:
    if not os.path.exists(sys.argv[1]):
        sys.exit("[ERROR] File %s was not found!" % sys.argv[1])
    else:
        EXPERIMENT_PARAMS_FILENAME = sys.argv[1]
        print "[INFO] Reproducing experiment with params: " + str(sys.argv[1])  
        REPRODUCE_EXPERIMENT = True    

#### SAVE EXPERIMENT PARAMS ####
TIME = time.strftime("%H:%M:%S")
DATE = time.strftime("%d.%b.%Y")

if SAVE_EXPERIMENT == True:
    FILENAME_WEIGHTS = "../../cross-validation/experiments/weights/motion_weights_" \
    + DATE + "_" + TIME +  ".npy"
    
    FILENAME_RESULTS = "../../cross-validation/experiments/results/motion_results_" \
    + DATE + "_" + TIME + ".csv"
    
    FILENAME_PARAMS = "../../cross-validation/experiments/params/motion_params_"   \
    + DATE + "_" + TIME  + ".csv"    
 
 
 # create instance of motion network
monet = libmotion.MotionNetwork()
 
#### EXPERIMENT PARAMS ####
if REPRODUCE_EXPERIMENT == True:
    #### REPRODUCE EXPERIMENT ####

    #extract params from file
    SOURCE_1, SOURCE_2, FILENAME_PRECOMPUTED_WEIGHTS, ROWS_1, COLS_1, \
    ROWS_2, COLS_2, ALPHA, LAMBDA, ACTUAL_IMAGES, \
    INTERPOLATION_TYPE = extract_params_from_file(EXPERIMENT_PARAMS_FILENAME)

    print "[INFO] Params extarcted from file"

    # create network
    monet.create_from_file(FILENAME_PRECOMPUTED_WEIGHTS, ROWS_1, COLS_1,
                           ROWS_2, COLS_2, ALPHA, LAMBDA, True)
    
    print "[INFO] Using loaded weight matrix"

      
    ############################################
else:         
    ##### CONFIGURE NEW EXPERIMENT ###########  
    ##### PARAMETERS ###########
  #  SOURCE_1 = "../../cross-validation/training/training_objects_minoru_0.avi"
  #  SOURCE_2 = "../../cross-validation/training/training_objects_minoru_1.avi"

    SOURCE_1 = "../../cross-validation/test/test_objects_30cm_30deg_0.avi"
    SOURCE_2 = "../../cross-validation/test/test_objects_30cm_30deg_1.avi"

    ROWS_1 = int(50)
    ROWS_2 = int(50)
    MVMNT_THRES = 20
    ACTUAL_IMAGES = False
    ALPHA = np.float32(1)
    LAMBDA =  np.float32(1)

    ##### CAMERA #####
    cap1 = cv2.VideoCapture(SOURCE_1)
    cap2 = cv2.VideoCapture(SOURCE_2)

    if not (cap1.isOpened() and cap2.isOpened()):
        raise NameError("[ERROR] Cannot extract images from video")    
        
    ret1, frame1 = cap1.read() # read = grab + retrieve (processing)
    ret2, frame2 = cap2.read() # read = grab + retrieve (processing)
    frame1_rows = frame1.shape[0]
    frame1_cols = frame1.shape[1]
    frame2_rows = frame2.shape[0]
    frame2_cols = frame2.shape[1]

    ##### NON TUNNEABLE PARAMETERS ###########
    COLS_1 = int(ROWS_1 * frame1_cols / frame1_rows)    
    COLS_2 = int(ROWS_2 * frame2_cols / frame2_rows)
    INTERPOLATION_TYPE = cv2.INTER_AREA
    ############################
    
    if EXTERNAL_WEIGHTS== True:
        monet.create_from_file(FILENAME_PRECOMPUTED_WEIGHTS, ROWS_1, COLS_1,
                           ROWS_2, COLS_2, ALPHA, LAMBDA, True)
        print "[INFO] Using loaded weight matrix"

    else:
        monet.create(ROWS_1, COLS_1, ROWS_2, COLS_2, ALPHA, LAMBDA)
        print "[INFO] Created new weight matrix"

    ############################
    
    
#### INITIALIZATION #########
image_1_t_1  =  np.zeros((ROWS_1, COLS_1), np.uint8) # image 1 previous time
image_2_t_1  =  np.zeros((ROWS_2, COLS_2), np.uint8) # image 2 previous time
error_image = np.zeros((ROWS_2,COLS_2), np.uint8) # first error map 2
fix_weights_matrix = False
ms_to_wait = int(1)
mse = [] 

##############################################################
############ LOOP ############################################
while(cap1.isOpened() and cap2.isOpened()):
    cap1.grab()
    cap2.grab()
    
    ret1, frame1 = cap1.retrieve()
    ret2, frame2 = cap2.retrieve()
 
    if(ret1==False or ret2==False):
        print "[ERROR] No stream of images (or end of file)"
        break
    
    # note the changed axis in opencv
    frame1_reduced  = cv2.resize(frame1,(COLS_1, ROWS_1), interpolation = INTERPOLATION_TYPE)
    frame2_reduced  = cv2.resize(frame2,(COLS_2, ROWS_2), interpolation = INTERPOLATION_TYPE)
    
    image_1_t_0 = cv2.cvtColor(frame1_reduced, cv2.COLOR_BGR2GRAY)
    image_2_t_0 = cv2.cvtColor(frame2_reduced, cv2.COLOR_BGR2GRAY)

    # 255.0 forcing float type
    var_img1 = (cv2.absdiff(image_1_t_0, image_1_t_1)/255.0).astype(np.float32)
    var_img2 = (cv2.absdiff(image_2_t_0, image_2_t_1)/255.0).astype(np.float32)
    
   
    #calculating total change in pixels
    total_change_img1 = int(sum(np.array(var_img1).flatten()))
    total_change_img2 = int(sum(np.array(var_img2).flatten()))    
    
  
    ######## update weights

    if REPRODUCE_EXPERIMENT == False and \
       fix_weights_matrix == False and \
       total_change_img1 > MVMNT_THRES and \
       total_change_img2 > MVMNT_THRES and \
       EXTERNAL_WEIGHTS== False:
           
         # update weights
         if ACTUAL_IMAGES == True:
             monet.train(image_1_t_0, image_2_t_0)
         else:
             monet.train(var_img1, var_img2)

    ###### calculate prediction image

    if ACTUAL_IMAGES == True:
         predictor_image_2 = monet.predict(image_1_t_0)
    else:
         predictor_image_2 = monet.predict(var_img1)

   #update previous image
    image_1_t_1 = image_1_t_0
    image_2_t_1 = image_2_t_0
    
###########################################
########### VISUALIZATION #################    
###########################################

    #### PREDICTOR MAPS ######
    predictor_image_2= predictor_image_2.astype(np.uint8)
    cv2.namedWindow('Predictor 2', cv2.WINDOW_NORMAL)     
    cv2.imshow('Predictor 2', predictor_image_2)

    #### SHOW ORIGINAL IMAGES ######
    cv2.namedWindow('Frame 1', cv2.WINDOW_NORMAL)     
    cv2.namedWindow('Frame 2', cv2.WINDOW_NORMAL)     

    if ACTUAL_IMAGES == True:
        cv2.imshow('Frame 1', image_1_t_0)
        cv2.imshow('Frame 2', image_2_t_0)
    else:
        cv2.imshow('Frame 1', var_img1)
        cv2.imshow('Frame 2', var_img2)
    
    #### ERROR MAPS ###### 
    cv2.namedWindow('Error (Frame 2, Prediction)', cv2.WINDOW_NORMAL)         

    if ACTUAL_IMAGES == True:
        error_image = cv2.absdiff(predictor_image_2, image_2_t_0)
    else:
        error_image = cv2.absdiff(predictor_image_2, (var_img2*255).astype(np.uint8))

    cv2.imshow('Error (Frame 2, Prediction)', error_image)


    if total_change_img1 > MVMNT_THRES and total_change_img2 > MVMNT_THRES:
        if ACTUAL_IMAGES == True:
            mse_value = monet.compute_mse(np.array(image_2_t_0).astype(np.float32), predictor_image_2)

        else:
            mse_value = monet.compute_mse(var_img2*255, predictor_image_2)
            
        mse.append(mse_value)


    ######### GRAB KEY AND EXIT (OPTIONALLY SAVING THE EXPERIMENT) #########
    k = cv2.waitKey(ms_to_wait) & 0xFF # dont use AND (logic), use & (bitwise)
    
    if k == ord('f'):
        fix_weights_matrix = True        
        print "[INFO] WeightsMatrix Fixed"

    if k == ord('s'):
        fix_weights_matrix = True        
        print "[INFO] Saving Images"
        if ACTUAL_IMAGES == True:
            cv2.imwrite( "../../cross-validation/experiments/outputs/motion_frame1_" \
            + DATE + "_" +  time.strftime("%H:%M:%S") +  ".png", image_1_t_0);
            
            cv2.imwrite( "../../cross-validation/experiments/outputs/motion_frame2_" \
            + DATE + "_" +  time.strftime("%H:%M:%S") +  ".png", image_2_t_0);
            
            cv2.imwrite( "../../cross-validation/experiments/outputs/motion_prediction2_" \
            + DATE + "_" +  time.strftime("%H:%M:%S") +  ".png", predictor_image_2);
        else: 
             cv2.imwrite( "../../cross-validation/experiments/outputs/motion_var1_" \
            + DATE + "_" +  time.strftime("%H:%M:%S") +  ".png", (var_img1*255).astype(np.uint8));           
            
             cv2.imwrite( "../../cross-validation/experiments/outputs/motion_var2_" \
            + DATE + "_" +  time.strftime("%H:%M:%S") +  ".png", (var_img2*255).astype(np.uint8));              
            
             cv2.imwrite( "../../cross-validation/experiments/outputs/motion_prediction2_" \
            + DATE + "_" +  time.strftime("%H:%M:%S") +  ".png", predictor_image_2);


    if k == ord('q'):                  
        break

#########################################################
#####################   END LOOP   #####################

if REPRODUCE_EXPERIMENT == True:
    print "[INFO] Removing decompressed file"
    os.remove(FILENAME_PRECOMPUTED_WEIGHTS.replace(".bz2", ""))  

if(SAVE_EXPERIMENT == True):
    print "[INFO] Saving experiment"         
    
    print "[INFO] Saving results"
    
    # save results
    file_results = open(FILENAME_RESULTS, "w")
    file_results.write("Mean Square Error\n")
    file_results.write("\n".join(map(lambda x: str(x), mse)))
    file_results.write("\n")            
    file_results.close()  

    print "[INFO] Saving params"
    
    # save params
    file_params = open(FILENAME_PARAMS, "w")
    list_params_names = ["SOURCE_1", "SOURCE_2", "FILENAME_WEIGHTS",
                          "FILENAME_RESULTS", "FILENAME_PARAMS","ROWS_1",
                          "COLS_1", "ROWS_2", "COLS_2", "ALPHA", "LAMBDA", 
                          "ACTUAL_IMAGES", "INTERPOLATION_TYPE"]
    
    list_params_values = [SOURCE_1, SOURCE_2, FILENAME_WEIGHTS + ".bz2", 
                         FILENAME_RESULTS, FILENAME_PARAMS, ROWS_1, 
                         COLS_1, ROWS_2, COLS_2, ALPHA, LAMBDA, 
                         ACTUAL_IMAGES, INTERPOLATION_TYPE]
                         
    file_params.write(",".join(map(lambda x: str(x), list_params_names)))
    file_params.write("\n")
    file_params.write(",".join(map(lambda x: str(x), list_params_values)))
    file_params.write("\n")
    file_params.close()           
    
    print "[INFO] Saving weights"
    
    # save weights matrix
    monet.save_weights_to_file(FILENAME_WEIGHTS, True)      
    
print "[INFO] Quitting program!"


cap1.release()
cap2.release()
cv2.destroyAllWindows()
