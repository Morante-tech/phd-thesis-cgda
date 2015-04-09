# -*- coding: utf-8 -*-
"""
Author: Santiago Morante
Robotics Lab. Universidad Carlos III de Madrid
About: This file (when finished) captures two videos, and trains weights
to relate both images. After training (in fact, it is online, so I should say
'when enough time has elapsed') it can predict movements between cameras.
"""

import numpy as np
from itertools import product
import cv2
import time
import csv
import sys
import os
import bz2
import fileinput

############################

REPRODUCE_EXPERIMENT = False    
EXPERIMENT_PARAMS_FILENAME = ""
SAVE_EXPERIMENT   = True

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
    FILENAME_PRECOMPUTED_WEIGHTS = experiment_list [1][2]
    ROWS_1 = int(experiment_list [1][5])
    COLS_1 = int(experiment_list [1][6])
    ROWS_2 = int(experiment_list [1][7])
    COLS_2 = int(experiment_list [1][8])
    ALPHA = float(experiment_list [1][9])
    BETA = float(experiment_list [1][10])
    if experiment_list [1][11] == "True":
        ACTUAL_IMAGES = True
    elif(experiment_list [1][11] == "False"):
        ACTUAL_IMAGES = False
    else:
        raise NameError("[ERROR] Undefined ACTUAL_IMAGES from file")    

    INTERPOLATION_TYPE = int(experiment_list [1][12])
    
    # decompress file and save it to ascii .net
    input_file = bz2.BZ2File(FILENAME_PRECOMPUTED_WEIGHTS, "rb")
    try:
        decompressed_filename = FILENAME_PRECOMPUTED_WEIGHTS.replace(".bz2", "")
        text_file = open(decompressed_filename, "w")
        text_file.write(input_file.read())
    
    finally:
        input_file.close()
        text_file.close()            
    
    # assign values to weights matrix
    weightMatrix = np.load(decompressed_filename).astype(np.float32)  
    np.ascontiguousarray(weightMatrix)    

    print "[INFO] Using loaded weight matrix"

    
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
else:         
    ##### CONFIGURE NEW EXPERIMENT ###########  
    ##  video
    SOURCE_1 = "../../raws/videos/sintel.avi"
    SOURCE_2 = "../../raws/videos/bunny.avi"

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

    ##### PARAMETERS ###########
    ROWS_1 = int(50)
    COLS_1 = int(ROWS_1 * frame1Cols / frame1Rows)
    ROWS_2 = int(50)
    COLS_2 = int(ROWS_2 * frame2Cols / frame2Rows)
    ALPHA = np.float32(0.05)
    BETA =  np.float32(0.5)
    ACTUAL_IMAGES = True
    INTERPOLATION_TYPE = cv2.INTER_AREA
    ############################
    weightMatrix = np.zeros((ROWS_1*ROWS_2, COLS_1*COLS_2), np.float32) # weight img
    np.ascontiguousarray(weightMatrix)    
    ############################
    
    
#### INITIALIZATION #########
ROWS_1_list = range(ROWS_1)
COLS_1_list = range(COLS_1)
image_1_t_1  =  np.zeros((ROWS_1, COLS_1), np.uint8) # image 1 previous time
image_2_t_1  =  np.zeros((ROWS_2, COLS_2), np.uint8) # image 2 previous time
error_image = np.zeros((ROWS_2,COLS_2), np.uint8) # first error map 2
totalWeights = np.zeros((ROWS_2,COLS_2), np.float32)
predictor_image_2 = np.zeros((ROWS_2,COLS_2), np.float32) # first predictor map 2
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
    
    #predictor image 2
    predictor_image_2 = 0
    
    # initialize total weights sum
    totalWeights = 0

    # update weights
    for (i,j) in product(ROWS_1_list, COLS_1_list):
       
        # find submatrix in DB and change currentweight value
        currWeightSubMatrixR2C2 = weightMatrix[i*ROWS_2:(i*ROWS_2+ROWS_2) ,
j*COLS_2:(j*COLS_2+COLS_2)].astype(np.float32)

        #if no variation in any of the images, we cannot predict relation
        #Similar to losing confidence in relation
        
        if(REPRODUCE_EXPERIMENT == False and fix_weights_matrix == False):
            #the elements that add value to the weights
            elem1  = ALPHA * var_img1.item(i,j) * var_img2
            elem2 = cv2.add(currWeightSubMatrixR2C2, elem1)
            
            #the elements that subtract value to the weights
            elem3 = cv2.absdiff(var_img1.item(i,j), var_img2)
            elem4 = elem3 * BETA
            
            #Subtraction of both elems
            elem5 = np.subtract(elem2,elem4)
            
            # limiting weights between 0 and 1
            newWeightSubMatrix = np.clip(elem5, 0, 1)
            
            #assign new weight to cell in DB
            weightMatrix[i*ROWS_2:(i*ROWS_2+ROWS_2), 
                         j*COLS_2:(j*COLS_2+COLS_2)] = newWeightSubMatrix
            
            totalWeights= cv2.add(totalWeights, newWeightSubMatrix)

        else:
            totalWeights= cv2.add(totalWeights, currWeightSubMatrixR2C2)

     ###### calculate prediction image
    for (i,j) in product(ROWS_1_list, COLS_1_list):   
        currWeightSubMatrixR2C2 = weightMatrix[i*ROWS_2:(i*ROWS_2+ROWS_2) , 
                                               j*COLS_2:(j*COLS_2+COLS_2)]
        
        if ACTUAL_IMAGES == True:
            img1DotWeight = np.multiply(image_1_t_0.item(i,j), currWeightSubMatrixR2C2)
        else:
            img1DotWeight = 255*np.multiply(var_img1.item(i,j), currWeightSubMatrixR2C2)
        
        img1DotWeightOverTotal =  np.divide(img1DotWeight, totalWeights)
        
        # avoid nan when dividing by zero
        img1DotWeightOverTotal = np.nan_to_num(img1DotWeightOverTotal)
        temp_pred_2= cv2.add(predictor_image_2 , img1DotWeightOverTotal)
        predictor_image_2 = np.clip(temp_pred_2, 0, 255)  

   #update previous image
    image_1_t_1 = image_1_t_0
    image_2_t_1 = image_2_t_0
    
###########################################
########### VISUALIZATION #################    
###########################################

    #### PREDICTOR MAPS ######
    adaptTypePredictor= predictor_image_2.astype(np.uint8)
    cv2.namedWindow('Predictor 2', cv2.WINDOW_NORMAL)     
    cv2.imshow('Predictor 2', adaptTypePredictor)

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
        error_image = cv2.absdiff(adaptTypePredictor, image_2_t_0)
        mse_temp_1 = cv2.absdiff(predictor_image_2, np.array(image_2_t_0).astype(np.float32))

    else:
        error_image = cv2.absdiff(adaptTypePredictor, (var_img2*255).astype(np.uint8))
        mse_temp_1 = cv2.absdiff(predictor_image_2, var_img2*255)

    cv2.imshow('Error (Frame 2, Prediction)', error_image)

    mse_temp_2 = np.square(mse_temp_1) / (ROWS_2*COLS_2)
    mse_value = sum( np.array(mse_temp_2).flatten() )
    mse.append(np.float32(mse_value))
    #print "[INFO] MSE: ", mse_value, "\n"

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
            + DATE + "_" + TIME +  ".png", image_1_t_0);
            
            cv2.imwrite( "../../cross-validation/experiments/outputs/motion_frame2_" \
            + DATE + "_" + TIME +  ".png", image_2_t_0);
            
            cv2.imwrite( "../../cross-validation/experiments/outputs/motion_prediction2_" \
            + DATE + "_" + TIME +  ".png", adaptTypePredictor);
        else: 
             cv2.imwrite( "../../cross-validation/experiments/outputs/motion_var1_" \
            + DATE + "_" + TIME +  ".png", var_img1);           
            
             cv2.imwrite( "../../cross-validation/experiments/outputs/motion_var2_" \
            + DATE + "_" + TIME +  ".png", var_img2);              
            
             cv2.imwrite( "../../cross-validation/experiments/outputs/motion_prediction2_" \
            + DATE + "_" + TIME +  ".png", adaptTypePredictor);


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
    file_results.write("\n".join(map(lambda x: str(x), mse)))
    file_results.write("\n")            
    file_results.close()  

    print "[INFO] Saving params"
    
    # save params
    file_params = open(FILENAME_PARAMS, "w")
    list_params_names = ["SOURCE_1", "SOURCE_2", "FILENAME_WEIGHTS",
                          "FILENAME_RESULTS", "FILENAME_PARAMS","ROWS_1",
                          "COLS_1", "ROWS_2", "COLS_2", "ALPHA", "BETA", 
                          "ACTUAL_IMAGES", "INTERPOLATION_TYPE"]
    
    list_params_values = [SOURCE_1, SOURCE_2, FILENAME_WEIGHTS, 
                         FILENAME_RESULTS, FILENAME_PARAMS, ROWS_1, 
                         COLS_1, ROWS_2, COLS_2, ALPHA, BETA, 
                         ACTUAL_IMAGES, INTERPOLATION_TYPE]
                         
    file_params.write(",".join(map(lambda x: str(x), list_params_names)))
    file_params.write("\n")
    file_params.write(",".join(map(lambda x: str(x), list_params_values)))
    file_params.write("\n")
    file_params.close()           
    
    print "[INFO] Saving weights"
    
    # save weights matrix
    np.save(FILENAME_WEIGHTS, weightMatrix)            
    
    # comprese and delete uncompressed file
    output = bz2.BZ2File(FILENAME_WEIGHTS + ".bz2", "wb")
     
    for line in fileinput.input(FILENAME_WEIGHTS):
            output.write(line)
    output.close()

    os.remove(FILENAME_WEIGHTS)          
    
print "[INFO] Quitting program!"


cap1.release()
cap2.release()
cv2.destroyAllWindows()
