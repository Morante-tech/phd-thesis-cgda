# -*- coding: utf-8 -*-
"""
Author: Santiago Morante
Robotics Lab. Universidad Carlos III de Madrid

About: This file (when finished) captures two videos, and trains weights
to relate both images. After training (in fact, it is online, so I should say
'when enough time has elapsed') it can predict movements between cameras.
"""

import numpy as np
import cv2
from fann2 import libfann
from fann2 import _libfann
import time
import csv
import sys
import os
import bz2
#import fileinput

############################

REPRODUCE_EXPERIMENT = False
EXPERIMENT_PARAMS_FILENAME = ""
SAVE_EXPERIMENT = True

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
    FILENAME_WEIGHTS = "../../cross-validation/experiments/weights/nn_weights_" \
    + DATE + "_" + TIME +  ".net"
    
    FILENAME_RESULTS = "../../cross-validation/experiments/results/nn_results_" \
    + DATE + "_" + TIME + ".csv"
    
    FILENAME_PARAMS = "../../cross-validation/experiments/params/nn_params_"   \
    + DATE + "_" + TIME  + ".csv"  
    
    
#### EXPERIMENT PARAMS ####
if REPRODUCE_EXPERIMENT == True:
    #### REPRODUCE EXPERIMENT ####
    experiment_list=[]
    with open(EXPERIMENT_PARAMS_FILENAME, "rb") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            experiment_list.append(row)
    print "[INFO] Experiment raw data: ", experiment_list [1]
    
    SOURCE_1 = experiment_list [1][0]
    SOURCE_2 = experiment_list [1][1]
    
    #overload temporal
    FILENAME_PRECOMPUTED_WEIGHTS = experiment_list [1][2]
    ROWS_1 = int(experiment_list [1][5])
    COLS_1 = int(experiment_list [1][6])
    ROWS_2 = int(experiment_list [1][7])
    COLS_2 = int(experiment_list [1][8])
    ALPHA = float(experiment_list [1][9])
    MOMENTUM = float(experiment_list [1][10])

    if experiment_list [1][11] == "True":
        HIDDEN = True
    elif(experiment_list [1][11] == "False"):
        HIDDEN = False
    else:
        raise NameError("[ERROR] Undefined HIDDEN from file")      
       
    TRAINING_ALGORITHM = int(experiment_list [1][12])
    TRAIN_ERROR_FUNCTION = int(experiment_list [1][13])
    TRAIN_STOP_FUNCTION = int(experiment_list [1][14])
    ACTIVATION_FUNCTION_HIDDEN = int(experiment_list [1][15])
    ACTIVATION_FUNCTION_OUTPUT = int(experiment_list [1][16])
    MVMNT_THRES = int(experiment_list [1][17])
    
    if experiment_list [1][18] == "True":
        ACTUAL_IMAGES = True
    elif(experiment_list [1][18] == "False"):
        ACTUAL_IMAGES = False
    else:
        raise NameError("[ERROR] Undefined ACTUAL_IMAGES from file")    

    INTERPOLATION_TYPE = int(experiment_list [1][19])

    print "[INFO] Using loaded neural network"    

    ##### CAMERA ###############################
    cap1 = cv2.VideoCapture(SOURCE_1)
    cap2 = cv2.VideoCapture(SOURCE_2)

    
    if not (cap1.isOpened() and cap2.isOpened()):
        raise NameError("[ERROR] Cannot extract images from video")    
        
    if isinstance(SOURCE_1,int) and isinstance(SOURCE_2,int):
        FPS = int(15)
        cap1.set(cv2.cv.CV_CAP_PROP_FPS, FPS)
        cap2.set(cv2.cv.CV_CAP_PROP_FPS, FPS)

    print "FPS Cap 1: ", cap1.get(cv2.cv.CV_CAP_PROP_FPS)
    print "FPS Cap 2: ", cap2.get(cv2.cv.CV_CAP_PROP_FPS)
    ############################################
    #########  NN ############
        
    # create ann
    ann = libfann.neural_net()
    
    # decompress file and save it to ascii .net
    input_file = bz2.BZ2File(FILENAME_PRECOMPUTED_WEIGHTS, "rb")
    try:
        decompressed_filename = FILENAME_PRECOMPUTED_WEIGHTS.replace(".bz2", "")
        text_file = open(decompressed_filename, "w")
        text_file.write(input_file.read())
    
    finally:
        input_file.close()
        text_file.close()        

    # assign values to ann
    ann.create_from_file(decompressed_filename)
    
    # Getting info from NN
    print "[INFO] sizes ann: ", ann.get_num_input(), " and ",  ann.get_num_output()
    print "[INFO] total number of neurons: " , ann.get_total_neurons()
    print "[INFO] total number of connections: " , ann.get_total_connections()
    print "[INFO] ann params: ", ann.print_parameters()


else:         
    ##### CONFIGURE NEW EXPERIMENT ###########  
    # tatup video
    SOURCE_1 = "../../raws/videos/sintel.avi"
    SOURCE_2 = "../../raws/videos/bunny.avi"
    
    ROWS_1 = int(50)
    ROWS_2 = int(50)
    ALPHA = float(0.05)
    MOMENTUM =  float(0.8)
    HIDDEN = True
    ACTUAL_IMAGES = False
    MVMNT_THRES = 10
    EXTERNAL_WEIGHTS = False
    FILENAME_PRECOMPUTED_WEIGHTS = ""
    
    
    ##### CAMERA #####
    cap1 = cv2.VideoCapture(SOURCE_1)
    cap2 = cv2.VideoCapture(SOURCE_2)

    
    if not (cap1.isOpened() and cap2.isOpened()):
        raise NameError("[ERROR] Cannot extract images from video")    
        
    if isinstance(SOURCE_1,int) and isinstance(SOURCE_2,int):
        FPS = int(15)
        cap1.set(cv2.cv.CV_CAP_PROP_FPS, FPS)
        cap2.set(cv2.cv.CV_CAP_PROP_FPS, FPS)
    
    print "FPS Cap 1: ", cap1.get(cv2.cv.CV_CAP_PROP_FPS)
    print "FPS Cap 2: ", cap2.get(cv2.cv.CV_CAP_PROP_FPS)
    
    ret1, frame1 = cap1.read() # read = grab + retrieve (processing)
    ret2, frame2 = cap2.read() # read = grab + retrieve (processing)
    frame1Rows = frame1.shape[0]
    frame1Cols = frame1.shape[1]
    frame2Rows = frame2.shape[0]
    frame2Cols = frame2.shape[1]
    
    ##### NON TUNNEABLE PARAMETERS ###########

    COLS_1 = int(ROWS_1 * frame1Cols / frame1Rows)
    COLS_2 = int(ROWS_2 * frame2Cols / frame2Rows)
    TRAINING_ALGORITHM   = _libfann.TRAIN_INCREMENTAL
    TRAIN_ERROR_FUNCTION = _libfann.ERRORFUNC_TANH
    TRAIN_STOP_FUNCTION  =_libfann.STOPFUNC_MSE
    ACTIVATION_FUNCTION_HIDDEN =_libfann.SIGMOID
    ACTIVATION_FUNCTION_OUTPUT = _libfann.SIGMOID
    INTERPOLATION_TYPE = cv2.INTER_AREA
    ############################


    #########  NN ############
    # setting
    ann = libfann.neural_net()
    
    if EXTERNAL_WEIGHTS== True:
        decompressed_filename = FILENAME_PRECOMPUTED_WEIGHTS.replace(".bz2", "")
    
        # assign values to ann
        ann.create_from_file(decompressed_filename)    
    else:
    
        if HIDDEN == True:
            ann.create_standard_array([ROWS_1*COLS_1,ROWS_1*COLS_1, ROWS_2*COLS_2])
            ann.set_activation_function_hidden(ACTIVATION_FUNCTION_HIDDEN)
        else:
            ann.create_standard_array([ROWS_1*COLS_1, ROWS_2*COLS_2])
        
        ann.set_learning_rate(ALPHA)
        ann.set_learning_momentum(MOMENTUM)
        ann.set_training_algorithm(TRAINING_ALGORITHM)
        ann.set_train_error_function(TRAIN_ERROR_FUNCTION)
        ann.set_train_stop_function(TRAIN_STOP_FUNCTION)
        ann.set_activation_function_output(ACTIVATION_FUNCTION_OUTPUT)
    
    # Getting info from NN
    print "[INFO] sizes ann: ", ann.get_num_input(), " and ",  ann.get_num_output()
    print "[INFO] total number of neurons: " , ann.get_total_neurons()
    print "[INFO] total number of connections: " , ann.get_total_connections()
    print "[INFO] ann params: ", ann.print_parameters()

       
######################################################

## INITIALIZATION ##
image_1_t_0  =  np.zeros((ROWS_1, COLS_1), np.uint8) # image 1 previous time
image_2_t_0  =  np.zeros((ROWS_2, COLS_2), np.uint8) # image 2 previous time
image_1_t_1  =  np.zeros((ROWS_1, COLS_1), np.uint8) # image 1 previous time
image_2_t_1  =  np.zeros((ROWS_2, COLS_2), np.uint8) # image 2 previous time
error_image = np.zeros((ROWS_2,COLS_2), np.uint8) # first error map 2
FIX_WEIGHTS_MATRIX = False
MS_TO_WAIT = int(1)
mse_own = [] 

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

    # variation image
    var_img1 = cv2.absdiff(image_1_t_0, image_1_t_1).astype(np.float32)
    var_img2 = cv2.absdiff(image_2_t_0, image_2_t_1).astype(np.float32)

    
    if ACTUAL_IMAGES == True:
        img1 = np.array(image_1_t_0).flatten().astype(np.float32) / 255.0 # normalize 0-1 for NN
        img2 = np.array(image_2_t_0).flatten().astype(np.float32) / 255.0 # normalize 0-1 for NN

        #calculating total change in pixels
        total_change_img1 = int(sum(np.array(var_img1).flatten() / 255.0))
        total_change_img2 = int(sum(np.array(var_img2).flatten() / 255.0))

    else:
        img1 = np.array(var_img1).flatten() / 255.0 # normalize 0-1 for NN
        img2 = np.array(var_img2).flatten() / 255.0 # normalize 0-1 for NN
        
        #calculating total change in pixels
        total_change_img1 = int(sum(img1))
        total_change_img2 = int(sum(img2))
    
    
    # train only if enough movement has ocurred
    if REPRODUCE_EXPERIMENT == False and FIX_WEIGHTS_MATRIX == False \
    and total_change_img1 > MVMNT_THRES and total_change_img2 > MVMNT_THRES:    
        ann.train(img1, img2)  #train 1 sample (incremental)
   
    ## PREDICTING SAMPLE
    predictor_image_2_list = ann.run(img1)
    
    ## UPDATE PREVIOUS IMAGES
    image_1_t_1 = image_1_t_0
    image_2_t_1 = image_2_t_0

###########################################
########### VISUALIZATION #################    
###########################################

    #### PREDICTOR MAPS ######
    predictor_image_2 = (255* np.array(predictor_image_2_list).reshape((ROWS_2, COLS_2))).astype(np.float32)
    adaptTypePredictor= predictor_image_2.astype(np.uint8)
   
    cv2.namedWindow('Predictor', cv2.WINDOW_NORMAL)     
    cv2.imshow('Predictor', adaptTypePredictor)

    #### SHOW ORIGINAL IMAGES ######
    cv2.namedWindow('Frame 1', cv2.WINDOW_NORMAL)     
    cv2.namedWindow('Frame 2', cv2.WINDOW_NORMAL)     

    if ACTUAL_IMAGES == True:
        cv2.imshow('Frame 1', image_1_t_0)
        cv2.imshow('Frame 2', image_2_t_0)    
    else:    
        cv2.imshow('Frame 1', var_img1.astype(np.uint8))
        cv2.imshow('Frame 2', var_img2.astype(np.uint8))    

    #### ERROR MAPS ###### 
    cv2.namedWindow('Error (Frame 2, Prediction)', cv2.WINDOW_NORMAL)         

    if ACTUAL_IMAGES == True:
        error_image = cv2.absdiff(adaptTypePredictor, image_2_t_0)
    else:
        error_image = cv2.absdiff(predictor_image_2, var_img2)
    
    cv2.imshow('Error (Frame 2, Prediction)', error_image.astype(np.uint8))
    
    mse_temp_1 = cv2.absdiff(predictor_image_2, image_2_t_0.astype(np.float32))
    mse_temp_2 = np.square(mse_temp_1) / (ROWS_2*COLS_2)
    mse_value = sum( np.array(mse_temp_2).flatten() )
    mse_own.append(np.float32(mse_value))
   # print "[INFO] MSE_OWN: ", mse_value

    #### Keys ###
    k = cv2.waitKey(MS_TO_WAIT) & 0xFF # not use AND (logic), use & (bitwise)
    if k == ord('f'):
        FIX_WEIGHTS_MATRIX = True        
        print '[INFO] WeightsMatrix Fixed'

    if k == ord('s'):
        fix_weights_matrix = True        
        print "[INFO] Saving Images"
        if ACTUAL_IMAGES == True:
            cv2.imwrite( "../../cross-validation/experiments/outputs/nn_frame1_" \
            + DATE + "_" + time.strftime("%H:%M:%S") +  ".png", image_1_t_0);
            
            cv2.imwrite( "../../cross-validation/experiments/outputs/nn_frame2_" \
            + DATE + "_" + time.strftime("%H:%M:%S") +  ".png", image_2_t_0);
            
            cv2.imwrite( "../../cross-validation/experiments/outputs/nn_prediction2_" \
            + DATE + "_" + time.strftime("%H:%M:%S") +  ".png", adaptTypePredictor);
        else: 
             cv2.imwrite( "../../cross-validation/experiments/outputs/nn_var1_" \
            + DATE + "_" + time.strftime("%H:%M:%S") +  ".png", var_img1.astype(np.uint8));           
            
             cv2.imwrite( "../../cross-validation/experiments/outputs/nn_var2_" \
            + DATE + "_" + time.strftime("%H:%M:%S") +  ".png", var_img2.astype(np.uint8));              
            
             cv2.imwrite( "../../cross-validation/experiments/outputs/nn_prediction2_" \
            + DATE + "_" + time.strftime("%H:%M:%S") +  ".png", adaptTypePredictor);



    if k == ord('q'):
        break
#########################################################
#####################   END LOOP   #####################
if REPRODUCE_EXPERIMENT == True:
    print "[INFO] Removing decompressed file"
    os.remove(decompressed_filename)  

if(SAVE_EXPERIMENT == True):
    print "[INFO] Saving experiment"
    print "[INFO] Saving results"

    # save results
    file_results = open(FILENAME_RESULTS, "w")
 

    file_results.write("Mean Square Error\n")
    
    for i in range(len(mse_own)):
        file_results.write(str(mse_own[i]) + "\n")            
    
    file_results.write("\n")            
    file_results.close()  
                 
    print "[INFO] Saving params"
                 
    # save params
    file_params = open(FILENAME_PARAMS, "w")
    list_params_names = ["SOURCE_1", "SOURCE_2", "FILENAME_WEIGHTS",
                          "FILENAME_RESULTS", "FILENAME_PARAMS","ROWS_1",
                          "COLS_1", "ROWS_2", "COLS_2", "ALPHA", "MOMENTUM", 
                          "HIDDEN", "TRAINING_ALGORITHM", 
                          "TRAIN_ERROR_FUNCTION", "TRAIN_STOP_FUNCTION",
                          "ACTIVATION_FUNCTION_HIDDEN", "ACTIVATION_FUNCTION_OUTPUT",
                          "MVMNT_THRES", "ACTUAL_IMAGES", "INTERPOLATION_TYPE"]
    
    list_params_values = [SOURCE_1, SOURCE_2, FILENAME_WEIGHTS,
                          FILENAME_RESULTS, FILENAME_PARAMS, ROWS_1,
                          COLS_1, ROWS_2, COLS_2, ALPHA, MOMENTUM, 
                          HIDDEN, TRAINING_ALGORITHM, 
                          TRAIN_ERROR_FUNCTION, TRAIN_STOP_FUNCTION,
                          ACTIVATION_FUNCTION_HIDDEN, ACTIVATION_FUNCTION_OUTPUT,
                          MVMNT_THRES, ACTUAL_IMAGES, INTERPOLATION_TYPE]
                         
    file_params.write(",".join(map(lambda x: str(x), list_params_names)))
    file_params.write("\n")
    file_params.write(",".join(map(lambda x: str(x), list_params_values)))
    file_params.write("\n")
    file_params.close()          
    
    print "[INFO] Saving weights"
    
    # save network
    ann.save(FILENAME_WEIGHTS)
    
#    # comprese and delete uncompressed file
#    output = bz2.BZ2File(FILENAME_WEIGHTS + ".bz2", "wb")
#     
#    for line in fileinput.input(FILENAME_WEIGHTS):
#            output.write(line)
#    output.close()
#
#    os.remove(FILENAME_WEIGHTS)            
    
print "[INFO] Quitting program!"


cap1.release()
cap2.release()
cv2.destroyAllWindows()