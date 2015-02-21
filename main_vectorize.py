# -*- coding: utf-8 -*-
"""
Author: Santiago Morante
Robotics Lab. Universidad Carlos III de Madrid

About: This file (when finished) captures two videos, and trains weights
to relate both images. After training (in fact, it is online, so I should say
'when enough time has passed') it can predict movements between cameras.
"""

import numpy as np
import cv2
from itertools import product
    

# from video
cap1 = cv2.VideoCapture('videos/synthetic.mp4')
cap2 = cv2.VideoCapture('videos/synthetic.mp4')

#from webcam
#cap1 = cv2.VideoCapture(2)
#cap2 = cv2.VideoCapture(1)


##### some variables ###############################
if(cap1.isOpened() & cap2.isOpened()):
    ret1, frame1 = cap1.read()
    ret2, frame2 = cap2.read()
    
    frame1Rows = frame1.shape[0]
    frame1Cols = frame1.shape[1]
    frame2Rows = frame2.shape[0]
    frame2Cols = frame2.shape[1]
else:
    raise NameError('Cannot extract images from video')    
######################################################

##### predictor params
ROWS_1 = int(20)
COLS_1 = int(ROWS_1 * frame1Cols / frame1Rows)
ROWS_2 = int(20)
COLS_2 = int(ROWS_2 * frame2Cols / frame2Rows)
alpha = np.float32(1)
beta =  np.float32(1)

####### file params
loadWeightsFromFile = False
saveWeightsToFile   = False
weightsFilename = 'data/weightMatrix' + str(ROWS_1)+ '-' + str(ROWS_2) + '.npy'
##############


###############################
if(loadWeightsFromFile==True):
    weightMatrix = np.load(weightsFilename).astype(np.float32)
else:    
    weightMatrix  =  np.zeros((ROWS_1*ROWS_2, COLS_1*COLS_2), np.float32) # weight img
####
np.ascontiguousarray(weightMatrix)    
## create dataframe                  
ROWS_1_list = range(ROWS_1)
COLS_1_list = range(COLS_1)
ROWS_2_list = range(ROWS_2)
COLS_2_list = range(COLS_2)

    
## some neccesary initialization
image_1_t_1  =  np.zeros((ROWS_1, COLS_1), np.uint8) # image 1 previous time
image_2_t_1  =  np.zeros((ROWS_2, COLS_2), np.uint8) # image 2 previous time
#error_image_2 = np.zeros((frame2Rows,frame2Cols), np.uint8) #first error map 2
totalWeights = np.zeros((ROWS_2,COLS_2), np.float32)
predictor_image_2 = np.zeros((ROWS_2,COLS_2), np.float32) #first predictor map 2

###############################
############ LOOP #############
while(cap1.isOpened() & cap2.isOpened()):
    ret1, frame1 = cap1.read()
    ret2, frame2 = cap2.read()
    if(ret1==False | ret2==False):
        print 'No stream of images!!'
        break
    
    # note the changed axis in opencv
    frame1_reduced  = cv2.resize(frame1,(COLS_1, ROWS_1), interpolation = cv2.INTER_NEAREST)
    frame2_reduced  = cv2.resize(frame2,(COLS_2, ROWS_2), interpolation = cv2.INTER_NEAREST)
    
    image_1_t_0 = cv2.cvtColor(frame1_reduced, cv2.COLOR_BGR2GRAY)
    image_2_t_0 = cv2.cvtColor(frame2_reduced, cv2.COLOR_BGR2GRAY)

    # 255.0 forcing float type
    var_img1 = (cv2.absdiff(image_1_t_0, image_1_t_1)/255.0).astype(np.float32)
    var_img2 = (cv2.absdiff(image_2_t_0, image_2_t_1)/255.0).astype(np.float32)
        
    predictor_image_2 = 0 #first predictor map 2
    
    # initialize total weights sum
    #totalWeights = np.zeros((ROWS_2,COLS_2))
    totalWeights = 0

    # update weights
    for (i,j) in product(ROWS_1_list, COLS_1_list):
       
        # find row in DB and change currentweight value
        currWeightSubMatrixR2C2 = weightMatrix[i*ROWS_2:(i*ROWS_2+ROWS_2) , j*COLS_2:(j*COLS_2+COLS_2)].astype(np.float32)

        #if no variation in any of the images, we cannot predict relation
        #so only decay affects output. Similar to losing confidence in 
        #relation (prediction)
        
        if(loadWeightsFromFile == False):
            #the elements adding
            elem1  = alpha * var_img1.item(i,j) * var_img2
            elem2 = cv2.add(currWeightSubMatrixR2C2, elem1)
            
            #the elements subtracting
            elem3 = cv2.absdiff(var_img1.item(i,j), var_img2)
            elem4 = elem3 * beta
            
            #final result
            elem5 = np.subtract(elem2,elem4)
            newWeightSubMatrix = np.clip(elem5, 0, 1)
            
            #assign new weight to cell in DB
            weightMatrix[i*ROWS_2:(i*ROWS_2+ROWS_2), j*COLS_2:(j*COLS_2+COLS_2)] = newWeightSubMatrix
            totalWeights= cv2.add(totalWeights, newWeightSubMatrix)
        else:
            totalWeights= cv2.add(totalWeights, currWeightSubMatrixR2C2)

     ###### calculate prediction image
    for (i,j) in product(ROWS_1_list, COLS_1_list):   
        currWeightSubMatrixR2C2 = weightMatrix[i*ROWS_2:(i*ROWS_2+ROWS_2) , j*COLS_2:(j*COLS_2+COLS_2)]
        img1DotWeight = np.multiply(image_1_t_0.item(i,j), currWeightSubMatrixR2C2)
        img1DotWeightOverTotal =  np.divide(img1DotWeight, totalWeights)
        temp_pred_2= cv2.add(predictor_image_2 , img1DotWeightOverTotal)
        predictor_image_2 = np.clip(temp_pred_2, 0, 255)  

   #update previous image
    image_1_t_1 = image_1_t_0
    image_2_t_1 = image_2_t_0
#########################################################
#####################   END LOOP   #####################
    
###########################################
########### VISUALIZATION #################    
###########################################

    
    #### PREDICTOR MAPS ######
    adaptTypePredictor= predictor_image_2.astype(np.uint8)
    predictorImg2 = cv2.resize(adaptTypePredictor,(frame2Cols,  frame2Rows), interpolation = cv2.INTER_NEAREST)
    cv2.imshow('Predictor 2', predictorImg2)

    #### SHOW ORIGINAL IMAGES ######
    cv2.imshow('Frame 1 (color)', frame1)
    smallerReducedImg2 = cv2.resize(image_2_t_0,(frame2Cols,  frame2Rows), interpolation = cv2.INTER_NEAREST)
    cv2.imshow('Frame 2 (Reduced, gray, then extended again)', smallerReducedImg2)
    
    
#    #### WEIGHT MAPS ####
#    adaptTypeWeight= cv2.multiply(weightMatrix, 255*255).astype(np.uint8)
#    cv2.imshow('WeightMatrix',adaptTypeWeight)

    #### ERROR MAPS ###### 
    error_image_2 = cv2.absdiff(predictorImg2, smallerReducedImg2)
    cv2.imshow('Error 2', error_image_2)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        if(saveWeightsToFile == True):
            np.save(weightsFilename, weightMatrix)
        break
#################################
######## END WHILE #############

cv2.destroyAllWindows()
