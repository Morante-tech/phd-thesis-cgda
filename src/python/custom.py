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
from itertools import product
import time

    
# tatup video
SOURCE_1 = "../../feed/videos/tatup.mp4"
'''
source 1, input to network
'''

SOURCE_2 = "../../feed/videos/tatup.mp4"
'''
source 2, output to network (to compare with prediction)
'''

## synthetic video
#SOURCE_1 = "../../feed/videos/synthetic2.ogg"
#SOURCE_2 = "../../feed/videos/synthetic2.ogg"
#
## webcam
#SOURCE_1 = 0
#SOURCE_2 = 1

# capture
cap1 = cv2.VideoCapture(SOURCE_1)
cap2 = cv2.VideoCapture(SOURCE_2)

if isinstance(SOURCE_1,int) and isinstance(SOURCE_2,int):
    cap1.set(cv2.cv.CV_CAP_PROP_FPS, 15)
    cap2.set(cv2.cv.CV_CAP_PROP_FPS, 15)


##### some variables ###############################
if(cap1.isOpened() & cap2.isOpened()):

    cap1.grab() # faster image adquisition than read
    cap2.grab() # faster image adquisition than read
    
    ret1, frame1 = cap1.retrieve() # read = grab + retrieve (processing)
    ret2, frame2 = cap2.retrieve() # read = grab + retrieve (processing)
    
    frame1Rows = frame1.shape[0]
    frame1Cols = frame1.shape[1]
    frame2Rows = frame2.shape[0]
    frame2Cols = frame2.shape[1]
else:
    raise NameError('[ERROR] Cannot extract images from video')    
######################################################

##### MAIN PARAMETERS ###########
ROWS_1 = int(40)
''' 
image 1 rows in reduced image to feed the network with
'''

COLS_1 = int(ROWS_1 * frame1Cols / frame1Rows)
''' 
image 1 cols in reduced image to feed the network with
'''

ROWS_2 = int(40)
''' 
image 2 rows in reduced image to feed the network with
'''

COLS_2 = int(ROWS_2 * frame2Cols / frame2Rows)
''' 
image 2 cols in reduced image to feed the network with
'''

ALPHA = np.float32(0.05)
'''
The learning rate is used to determine how aggressive training should be
'''

BETA =  np.float32(0.5)
'''
Determine the decay, it counterweights alpha
'''

FIX_WEIGHTS_MATRIX = False
'''
This param is used to fix the network in a specific moment, 
and dont train it more
'''

ACTUAL_IMAGES = False
'''
it determines wheter to predict variations or images
'''

MS_TO_WAIT = int(1)
'''
ms to wait for a key in opencv
'''

INTERPOLATION_TYPE = cv2.INTER_AREA
'''
INTER_NEAREST - a nearest-neighbor interpolation
INTER_LINEAR - a bilinear interpolation (used by default)
INTER_AREA - resampling using pixel area relation. 
      It may be a preferred method for image decimation, as it gives moire’-free results. 
      But when the image is zoomed, it is similar to the INTER_NEAREST method.
INTER_CUBIC - a bicubic interpolation over 4x4 pixel neighborhood. slow better to enlarge
INTER_LANCZOS4 - a Lanczos interpolation over 8x8 pixel neighborhood
'''

LOAD_WEIGHTS_FROM_FILE = False
'''
To load from file the weights matrix
'''

SAVE_EXPERIMENTS   = False
'''
To save WEIGHTS, PARAMS AND RESULTS
'''

TIME = time.strftime("%H:%M:%S")
'''
time of the experiment
'''
 
DATE = time.strftime("%d.%b.%Y")
'''
date of the experiment
'''

FILENAME_WEIGHTS = '../../cross-validation/experiments/weights/custom_weights_' \
+ DATE + '_' + TIME +  '.npy'
'''
filename to save the weights matrix
'''

FILENAME_RESULTS = '../../cross-validation/experiments/results/custom_results_' \
+ DATE + '_' + TIME + '.csv'
'''
filename to save the results
'''

FILENAME_PARAMS = '../../cross-validation/experiments/params/custom_params_'   \
+ DATE + '_' + TIME  + '.md'
'''
filename to save the params
'''
###############################

### LOADING FROM FILE ###
weight_path = "../../cross-validation/experiments/weights/"
weigth_name = "custom_weights_19.Mar.2015_16:12:22.npy"
if(LOAD_WEIGHTS_FROM_FILE==True):
    weightMatrix = np.load(weight_path + weigth_name).astype(np.float32) 
    print "[INFO] Using loaded weight matrix"
else:    
    weightMatrix  =  np.zeros((ROWS_1*ROWS_2, COLS_1*COLS_2), np.float32) # weight img

np.ascontiguousarray(weightMatrix)    
###############################

## create dataframe                  
ROWS_1_list = range(ROWS_1)
COLS_1_list = range(COLS_1)

## some neccesary initialization
image_1_t_1  =  np.zeros((ROWS_1, COLS_1), np.uint8) # image 1 previous time
image_2_t_1  =  np.zeros((ROWS_2, COLS_2), np.uint8) # image 2 previous time
error_image = np.zeros((ROWS_2,COLS_2), np.uint8) # first error map 2
totalWeights = np.zeros((ROWS_2,COLS_2), np.float32)
predictor_image_2 = np.zeros((ROWS_2,COLS_2), np.float32) # first predictor map 2
mse = [] 

###############################
############ LOOP #############
while(cap1.isOpened() and cap2.isOpened()):
    cap1.grab()
    cap2.grab()
    
    ret1, frame1 = cap1.retrieve()
    ret2, frame2 = cap2.retrieve()
 
    if(ret1==False or ret2==False):
        print '[ERROR] No stream of images!!'
        break
    
    # note the changed axis in opencv
    frame1_reduced  = cv2.resize(frame1,(COLS_1, ROWS_1), interpolation = INTERPOLATION_TYPE)
    frame2_reduced  = cv2.resize(frame2,(COLS_2, ROWS_2), interpolation = INTERPOLATION_TYPE)
    
    image_1_t_0 = cv2.cvtColor(frame1_reduced, cv2.COLOR_BGR2GRAY)
    image_2_t_0 = cv2.cvtColor(frame2_reduced, cv2.COLOR_BGR2GRAY)

    # 255.0 forcing float type
    var_img1 = (cv2.absdiff(image_1_t_0, image_1_t_1)/255.0).astype(np.float32)
    var_img2 = (cv2.absdiff(image_2_t_0, image_2_t_1)/255.0).astype(np.float32)
        
    predictor_image_2 = 0 #first predictor map 2
    
    # initialize total weights sum
    totalWeights = 0

    # update weights
    for (i,j) in product(ROWS_1_list, COLS_1_list):
       
        # find submatrix in DB and change currentweight value
        currWeightSubMatrixR2C2 = weightMatrix[i*ROWS_2:(i*ROWS_2+ROWS_2) ,
j*COLS_2:(j*COLS_2+COLS_2)].astype(np.float32)

        #if no variation in any of the images, we cannot predict relation
        #Similar to losing confidence in relation
        
        if(LOAD_WEIGHTS_FROM_FILE == False and FIX_WEIGHTS_MATRIX == False):
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

    mse_temp_2 = cv2.multiply(mse_temp_1, mse_temp_1) / (ROWS_2*COLS_2)
    mse_value = sum(np.array(mse_temp_2).flatten())
    #print "[INFO] MSE: ", mse_value, "\n"
    mse.append(np.float32(mse_value))

    ######### GRAB KEY AND EXIT (OPTIONALLY SAVING THE EXPERIMENT)    
    k = cv2.waitKey(MS_TO_WAIT) & 0xFF # dont use AND (logic), use & (bitwise)
    
    if k == ord('f'):
        FIX_WEIGHTS_MATRIX = True        
        print "[INFO] WeightsMatrix Fixed"

    if k == ord('q'):
        if(SAVE_EXPERIMENTS == True):
            print "[INFO] Saving experiment"

            np.save(FILENAME_WEIGHTS, weightMatrix)
            
            file_results = open(FILENAME_RESULTS, "w")
            file_results.write("Mean Square Error\n")
            file_results.write("\n".join(map(lambda x: str(x), mse)))
            file_results.close()  
            
            file_params = open(FILENAME_PARAMS, "w")
            text_params = \
"## Experiment Parameters \n\n" + \
"* **SOURCE_1 = " + str(SOURCE_1) + "**\n\n" + \
"source 1, input to network" + "\n\n" + \
"* **SOURCE_2 = " + str(SOURCE_2) + "**\n\n" + \
"source 2, output to network (to compare with prediction)" + "\n\n" + \
"* **FILENAME_WEIGHTS = " + str(FILENAME_WEIGHTS) + "**\n\n" + \
"filename to save the weights matrix" + "\n\n" + \
"* **FILENAME_RESULTS = " + str(FILENAME_RESULTS) + "**\n\n" + \
"filename to save the results" + "\n\n" + \
"* **FILENAME_PARAMS = " + str(FILENAME_PARAMS) + "**\n\n" + \
"filename to save the params" + "\n\n" + \
"* ROWS_1 = " + str(ROWS_1) + "\n\n" + \
"image 1 rows in reduced image to feed the network with" + "\n\n" + \
"* COLS_1 = " + str(COLS_1) + "\n\n" + \
"image 1 cols in reduced image to feed the network with" + "\n\n" + \
"* ROWS_2 = " + str(ROWS_2) + "\n\n" + \
"image 2 rows in reduced image to feed the network with" + "\n\n" + \
"* COLS_2 = " + str(COLS_2) + "\n\n" + \
"image 2 cols in reduced image to feed the network with" + "\n\n" + \
"* ALPHA = " + str(ALPHA) + "\n\n" + \
"The learning rate is used to determine how aggressive training should be" + "\n\n" + \
"* BETA =  " + str(BETA) + "\n\n" + \
"Determine the decay, it counterweights alpha" + "\n\n" + \
"* ACTUAL_IMAGES = " + str(ACTUAL_IMAGES) + "\n\n" + \
"it determines wheter to predict variations or images" + "\n\n" + \
"* INTERPOLATION_TYPE = " + str(INTERPOLATION_TYPE) + "\n\n" + \
"INTER_NEAREST - a nearest-neighbor interpolation \n\
INTER_LINEAR - a bilinear interpolation (used by default) \n\
INTER_AREA - resampling using pixel area relation.  It may be a preferred \
method for image decimation, as it gives moire’-free results. But when the \
image is zoomed, it is similar to the INTER_NEAREST method. \n\
INTER_CUBIC - a bicubic interpolation over 4x4 pixel neighborhood. slow better to enlarge \n\
INTER_LANCZOS4 - a Lanczos interpolation over 8x8 pixel neighborhood" + "\n\n"
            file_params.write(text_params)
            file_params.close()            
            
        print "[INFO] Quitting program!"
        break

#########################################################
#####################   END LOOP   #####################

cap1.release()
cap2.release()

cv2.destroyAllWindows()
