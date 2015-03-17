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

#from webcam
cap1 = cv2.VideoCapture(0)
cap2 = cv2.VideoCapture(1)

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
COLS_1 = int(ROWS_1 * frame1Cols / frame1Rows)
ROWS_2 = int(40)
COLS_2 = int(ROWS_2 * frame2Cols / frame2Rows)
alpha = float(0.7) 
momentum = float(0.0)
hidden = False

mvmnt_thres = 10
fixWeightsMatrix   = False
msToWait = int(1)
interpolationType = cv2.INTER_AREA
'''
INTER_NEAREST - a nearest-neighbor interpolation
INTER_LINEAR - a bilinear interpolation (used by default)
INTER_AREA - resampling using pixel area relation. 
      It may be a preferred method for image decimation, as it gives moire’-free results. 
      But when the image is zoomed, it is similar to the INTER_NEAREST method.
INTER_CUBIC - a bicubic interpolation over 4x4 pixel neighborhood. slow better to enlarge
INTER_LANCZOS4 - a Lanczos interpolation over 8x8 pixel neighborhood
'''
##### CAMS PARAMS #####
cap1.set(cv2.cv.CV_CAP_PROP_FPS, 15)
cap2.set(cv2.cv.CV_CAP_PROP_FPS, 15)
############################

## some neccesary initialization
image_1_t_0  =  np.zeros((ROWS_1, COLS_1), np.uint8) # image 1 previous time
image_2_t_0  =  np.zeros((ROWS_2, COLS_2), np.uint8) # image 2 previous time
image_1_t_1  =  np.zeros((ROWS_1, COLS_1), np.uint8) # image 1 previous time
image_2_t_1  =  np.zeros((ROWS_2, COLS_2), np.uint8) # image 2 previous time
error_image_2 = np.zeros((ROWS_2,COLS_2), np.uint8) # first error map 2
##########################

#########  NN ############
##########################

# setting
ann = libfann.neural_net()
if hidden == True:
    ann.create_standard_array([ROWS_1*COLS_1,ROWS_1*COLS_1, ROWS_2*COLS_2])
else:
    ann.create_standard_array([ROWS_1*COLS_1, ROWS_2*COLS_2])
ann.set_training_algorithm(_libfann.TRAIN_INCREMENTAL)
'''
TRAIN_RPROP
TRAIN_INCREMENTAL
'''
ann.set_learning_momentum(momentum)
ann.set_learning_rate(alpha)
ann.set_train_error_function(_libfann.ERRORFUNC_TANH)
#ann.set_activation_function_output(_libfann.SIGMOID_SYMMETRIC)

# getting
print "[INFO] sizes: ", ROWS_1*COLS_1, " and ", ROWS_2*COLS_2
print "[INFO] sizes ann: ", ann.get_num_input(), " and ",  ann.get_num_output()
print "[INFO] total number of neurons: " , ann.get_total_neurons()
print "[INFO] total number of connections: " , ann.get_total_connections()
print "[INFO] ann params: ", ann.print_parameters()

##############################################################
############ LOOP ############################################
while(cap1.isOpened() and cap2.isOpened()):
    cap1.grab()
    cap2.grab()
    
    ret1, frame1 = cap1.retrieve()
    ret2, frame2 = cap2.retrieve()
 
    if(ret1==False or ret2==False):
        print '[ERROR] No stream of images!!'
        break
    
    # note the changed axis in opencv
    frame1_reduced  = cv2.resize(frame1,(COLS_1, ROWS_1), interpolation = interpolationType)
    frame2_reduced  = cv2.resize(frame2,(COLS_2, ROWS_2), interpolation = interpolationType)
    
    image_1_t_0 = cv2.cvtColor(frame1_reduced, cv2.COLOR_BGR2GRAY)
    image_2_t_0 = cv2.cvtColor(frame2_reduced, cv2.COLOR_BGR2GRAY)


# variation image
    var_img1 = cv2.absdiff(image_1_t_0, image_1_t_1)
    var_img2 = cv2.absdiff(image_2_t_0, image_2_t_1)

    img1 = np.array(var_img1).flatten().astype(np.float32) / 255.0 # normalize 0-1 for NN
    img2 = np.array(var_img1).flatten().astype(np.float32) / 255.0 # normalize 0-1 for NN
    
    total_change_img1 = int(sum(img1))
    total_change_img2 = int(sum(img2))
    
    print "[INFO] Sum movement 1: ", total_change_img1
    print "[INFO] Sum movement 2: ", total_change_img2, "\n"
    
    #train only if enough movement is available
    if fixWeightsMatrix == False and total_change_img1 > mvmnt_thres and total_change_img2 > mvmnt_thres:    
        ann.train(img1, img2)  #train 1 sample (incremental)
    print "[INFO] MSE: ", ann.get_MSE()

    predictor_image_2_list = ann.run(img1)    # predict 1 sample
    

    image_1_t_1 = image_1_t_0       #update previous image
    image_2_t_1 = image_2_t_0      #update previous image

###########################################
########### VISUALIZATION #################    
###########################################

    #### PREDICTOR MAPS ######
    # des-normalizing and reshaping
    predictor_image_2 = 255 * np.array(predictor_image_2_list).reshape((ROWS_2, COLS_2))
    adaptTypePredictor= predictor_image_2.astype(np.uint8)
   
    cv2.namedWindow('Predictor 2', cv2.WINDOW_NORMAL)     
    cv2.imshow('Predictor 2', adaptTypePredictor)

    #### SHOW ORIGINAL IMAGES ######

  
    cv2.namedWindow('Frame 1 (Reduced, gray, then extended again)', cv2.WINDOW_NORMAL)     
    cv2.imshow('Frame 1 (Reduced, gray, then extended again)', var_img1)

    cv2.namedWindow('Frame 2 (Reduced, gray, then extended again)', cv2.WINDOW_NORMAL)     
    cv2.imshow('Frame 2 (Reduced, gray, then extended again)', var_img2)    
 
    
    #### ERROR MAPS ###### 
    
    error_image_2 = cv2.absdiff(adaptTypePredictor, var_img2)
    cv2.namedWindow('Error 2', cv2.WINDOW_NORMAL)         
    cv2.imshow('Error 2', error_image_2)

    #### Keys ###
    k = cv2.waitKey(msToWait) & 0xFF # not use AND, use &
    if k == ord('f'):
        fixWeightsMatrix = True        
        print '[INFO] WeightsMatrix Fixed'

    if k == ord('q'):
        break

#########################################################
#####################   END LOOP   #####################

cap1.release()
cap2.release()
cv2.destroyAllWindows()