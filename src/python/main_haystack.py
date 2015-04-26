# -*- coding: utf-8 -*-
"""
Author: Santiago Morante
Robotics Lab. Universidad Carlos III de Madrid
About: This file (when finished) captures two videos, and trains weights
to relate both images. After training (in fact, it is online, so I should say
'when enough time has elapsed') it can predict movements between cameras.
"""

import numpy as np
import libhaystack
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
    
    mvmnt_thres = int(experiment_list [1][12])
    return (input_matrix, output_matrix, filename_precomputed_weights,
    input_rows, input_cols, output_rows, output_cols, alpha_param, lambda_param,
    actual_images, mvmnt_thres)


def reduce_and_gray(image, desired_rows, desired_cols):
    # note the changed axis in opencv
    image  = cv2.resize(image,(desired_cols, desired_rows), interpolation = cv2.INTER_AREA)    
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return image

def normalize_matrix(raw_matrix, max_value):
    return np.float32(raw_matrix) / max_value


def save_results(filename, mse_list):
    file_results = open(filename, "w")
    file_results.write("Mean Square Error\n")
    file_results.write("\n".join(map(lambda x: str(x), mse_list)))
    file_results.write("\n")            
    file_results.close()  

def save_params(list_params_names, list_params_values):
    file_params = open(FILENAME_PARAMS, "w")           
    file_params.write(",".join(map(lambda x: str(x), list_params_names)))
    file_params.write("\n")
    file_params.write(",".join(map(lambda x: str(x), list_params_values)))
    file_params.write("\n")
    file_params.close()           


############################

REPRODUCE_EXPERIMENT = False    
EXPERIMENT_PARAMS_FILENAME = ""
SAVE_EXPERIMENT   = True
EXTERNAL_WEIGHTS = False
FILENAME_PRECOMPUTED_WEIGHTS = ""
TIME = time.strftime("%H:%M:%S")
DATE = time.strftime("%d.%b.%Y")

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


 # create instance of motion network
monet = libhaystack.Network()
 
if REPRODUCE_EXPERIMENT == True:
    #### REPRODUCE EXPERIMENT ####
    #extract params from file
    SOURCE_1, SOURCE_2, FILENAME_PRECOMPUTED_WEIGHTS, INPUT_ROWS, INPUT_COLS, \
    OUTPUT_ROWS, OUTPUT_COLS, ALPHA, LAMBDA, ACTUAL_IMAGES, \
    MVMNT_THRES = extract_params_from_file(EXPERIMENT_PARAMS_FILENAME)

    print "[INFO] Params extracted from file"

    ##### CAMERA #####
    cap1 = cv2.VideoCapture(SOURCE_1)
    cap2 = cv2.VideoCapture(SOURCE_2)

    # create network
    monet.create_from_file(FILENAME_PRECOMPUTED_WEIGHTS+".bz2", INPUT_ROWS, INPUT_COLS,
                           OUTPUT_ROWS, OUTPUT_COLS, ALPHA, LAMBDA, True)
    
    print "[INFO] Using loaded weight matrix"
    
else:         
    ##### CONFIGURE NEW EXPERIMENT ###########  
    SOURCE_1 = "../../raws/videos/sintel.avi"
    SOURCE_2 = "../../raws/videos/sintel.avi"

    INPUT_ROWS = 50
    OUTPUT_ROWS = 50
    MVMNT_THRES = 20
    ACTUAL_IMAGES = True
    ALPHA = 0.05
    LAMBDA =  0.5
    # perfect params actual images (0.05, 0.5)
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
    INPUT_COLS = int(INPUT_ROWS * frame1_cols / frame1_rows)    
    OUTPUT_COLS = int(OUTPUT_ROWS * frame2_cols / frame2_rows) 
    
    if EXTERNAL_WEIGHTS== True:
        monet.create_from_file(FILENAME_PRECOMPUTED_WEIGHTS, INPUT_ROWS, INPUT_COLS,
                           OUTPUT_ROWS, OUTPUT_COLS, ALPHA, LAMBDA, True)
        print "[INFO] Using loaded weight matrix"

    else:
        monet.create(INPUT_ROWS, INPUT_COLS, OUTPUT_ROWS, OUTPUT_COLS, ALPHA, LAMBDA)
        print "[INFO] Created new weight matrix"
    
#### INITIALIZATION #########
image_1_t_1  =  np.zeros((INPUT_ROWS, INPUT_COLS), np.uint8) # image 1 previous time
image_2_t_1  =  np.zeros((OUTPUT_ROWS, OUTPUT_COLS), np.uint8) # image 2 previous time
fix_weights_matrix = False
mse = [] 
index = 0
############ LOOP ############
while(True):
    index+=1
    
    if index == 200 :
        fix_weights_matrix = True
    elif index == 400:
        break
    
    # read from cam
    cap1.grab()
    cap2.grab()

    ret1, frame1 = cap1.retrieve()
    ret2, frame2 = cap2.retrieve()
 
    if(ret1==False or ret2==False):
        print "[ERROR] No stream of images (or end of file)"
        break
    
    # reduced and gray
    image_1_t_0 = reduce_and_gray(frame1, INPUT_ROWS, INPUT_COLS)
    image_2_t_0 = reduce_and_gray(frame2, OUTPUT_ROWS, OUTPUT_COLS)

    # calculate variation
    variation_cap1 = (cv2.absdiff(image_1_t_0, image_1_t_1)).astype(np.float32)
    variation_cap2 = (cv2.absdiff(image_2_t_0, image_2_t_1)).astype(np.float32)
    
    # normalize
    normalized_variation_cap1 = normalize_matrix(variation_cap1, 255)   
    normalized_variation_cap2 = normalize_matrix(variation_cap2, 255)
    normalized_image_1_t_0 = normalize_matrix(image_1_t_0, 255)
    normalized_image_2_t_0 = normalize_matrix(image_2_t_0, 255) 

    # calculating total change in pixels
    total_change_img1 = np.sum(normalized_variation_cap1)
    total_change_img2 = np.sum(normalized_variation_cap2)   
    
    # update weights
    if REPRODUCE_EXPERIMENT == False and \
       fix_weights_matrix == False and \
       total_change_img1 > MVMNT_THRES and \
       total_change_img2 > MVMNT_THRES and \
       EXTERNAL_WEIGHTS == False:
           
         # update weights
         monet.train(normalized_variation_cap1, normalized_variation_cap2)
         
    # calculate prediction image
    if ACTUAL_IMAGES == True:
         predicted_output = monet.predict(normalized_image_1_t_0)
    else:
         predicted_output = monet.predict(normalized_variation_cap1)

    # calculate mean square error
    if total_change_img1 > MVMNT_THRES and total_change_img2 > MVMNT_THRES:
        if ACTUAL_IMAGES == True:
            mse_value = monet.compute_mse(normalized_image_2_t_0, predicted_output)
        else:
            mse_value = monet.compute_mse(normalized_variation_cap2, predicted_output)
            
        mse.append(mse_value)

    # update previous image
    image_1_t_1 = image_1_t_0
    image_2_t_1 = image_2_t_0
    
    ####### VISUALIZATION #################    
    cv2.namedWindow('Predicted output', cv2.WINDOW_NORMAL)     
    cv2.namedWindow('Input Image', cv2.WINDOW_NORMAL)     
    cv2.namedWindow('Output Image', cv2.WINDOW_NORMAL)     
    cv2.namedWindow('Error', cv2.WINDOW_NORMAL)         

    if ACTUAL_IMAGES == True:
        cv2.imshow('Input Image', image_1_t_0)
        cv2.imshow('Output Image', image_2_t_0)
        error_image = cv2.absdiff(predicted_output, normalized_image_2_t_0)

    else:
        cv2.imshow('Input Image', variation_cap1.astype(np.uint8))
        cv2.imshow('Output Image', variation_cap2.astype(np.uint8))
        error_image = cv2.absdiff(predicted_output, normalized_variation_cap2)
           
    cv2.imshow('Error', (error_image*255).astype(np.uint8))
    cv2.imshow('Predicted output', (predicted_output*255).astype(np.uint8))

    ##### GRAB KEY AND EXIT #########
    k = cv2.waitKey(1) & 0xFF # dont use AND (logic), use & (bitwise)
  
    if k == ord('q'):                  
        break
  
    if k == ord('f'):
        fix_weights_matrix = True        
        print "[INFO] WeightsMatrix Fixed"

    if k == ord('s'):
        print "[INFO] Saving Images"
        if ACTUAL_IMAGES == True:
            cv2.imwrite( "../../cross-validation/experiments/outputs/motion_input_" \
            + DATE + "_" +  time.strftime("%H:%M:%S") +  ".png", image_1_t_0);
            
            cv2.imwrite( "../../cross-validation/experiments/outputs/motion_output_" \
            + DATE + "_" +  time.strftime("%H:%M:%S") +  ".png", image_2_t_0);
            
        else: 
             cv2.imwrite( "../../cross-validation/experiments/outputs/motion_input_" \
            + DATE + "_" +  time.strftime("%H:%M:%S") +  ".png", variation_cap1);           
            
             cv2.imwrite( "../../cross-validation/experiments/outputs/motion_output_" \
            + DATE + "_" +  time.strftime("%H:%M:%S") +  ".png", variation_cap2);              
            
        cv2.imwrite( "../../cross-validation/experiments/outputs/motion_predicted_output_" \
        + DATE + "_" +  time.strftime("%H:%M:%S") +  ".png", (predicted_output*255).astype(np.uint8));

################  END LOOP  #####################
cap1.release()
cap2.release()
cv2.destroyAllWindows()

if SAVE_EXPERIMENT == True:
    print "[INFO] Saving experiment"         

    # save results
    print "[INFO] Saving results"    
    FILENAME_RESULTS = "../../cross-validation/experiments/results/motion_results_" \
    + DATE + "_" + TIME + ".csv"
    
    save_results(FILENAME_RESULTS, mse)
    
    # save weights matrix
    print "[INFO] Saving weights"
    FILENAME_WEIGHTS = "../../cross-validation/experiments/weights/motion_weights_" \
    + DATE + "_" + TIME +  ".npy"
    monet.save_weights_to_file(FILENAME_WEIGHTS, True)      

    # save params
    print "[INFO] Saving params"
    FILENAME_PARAMS = "../../cross-validation/experiments/params/motion_params_"   \
    + DATE + "_" + TIME  + ".csv"       
    
    list_params_names = ["SOURCE_1", "SOURCE_2", "FILENAME_WEIGHTS",
                          "FILENAME_RESULTS", "FILENAME_PARAMS","INPUT_ROWS",
                          "INPUT_COLS", "OUTPUT_ROWS", "OUTPUT_COLS", "ALPHA", "LAMBDA", 
                          "ACTUAL_IMAGES", "MOVEMENT_THRESHOLD"]
    
    list_params_values = [SOURCE_1, SOURCE_2, FILENAME_WEIGHTS, 
                         FILENAME_RESULTS, FILENAME_PARAMS, INPUT_ROWS, 
                         INPUT_COLS, OUTPUT_ROWS, OUTPUT_COLS, ALPHA, LAMBDA, 
                         ACTUAL_IMAGES, MVMNT_THRES]
    
    save_params(list_params_names, list_params_values)
 
# cleaning
if REPRODUCE_EXPERIMENT == True or EXTERNAL_WEIGHTS == True:
    print "[INFO] Removing decompressed file"
    temp = FILENAME_PRECOMPUTED_WEIGHTS.replace(".bz2", "")
    os.remove(FILENAME_PRECOMPUTED_WEIGHTS.replace(".bz2", ""))  
    
print "[INFO] Bye, bye!"