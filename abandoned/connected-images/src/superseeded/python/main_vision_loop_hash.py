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

################################################
################################################
def limit(x):
    if(x<=0):
        return 0
    elif(x>=1):
        return 1
    else:
        return x
      
################################################
################################################
    
#params
ROWS_1 = 10
COLS_1 = 10
ROWS_2 = 10
COLS_2 = 10

alpha = 0.2
beta =0.001

# video
cap1 = cv2.VideoCapture('videos/tatup.mp4')
cap2 = cv2.VideoCapture('videos/tatup.mp4')

# create dictionary (hash table)
data={}
ROWS_1_list = list(range(ROWS_1))
COLS_1_list = list(range(COLS_1))
ROWS_2_list = list(range(ROWS_2))
COLS_2_list = list(range(COLS_2))

combos = product(ROWS_1_list, COLS_1_list, ROWS_2_list, COLS_2_list)

#### filling initial data
for x in combos:
   theKey = str(x[0]) + " " + str(x[1]) + " " + str(x[2]) + " " + str(x[3])
   data[theKey]=0
######################################


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
    
## some neccesary initialization
image_1_t_1  =  np.zeros((ROWS_1, COLS_1), np.uint8) # image 1 previous time
image_2_t_1  =  np.zeros((ROWS_2, COLS_2), np.uint8) # image 2 previous time

predictor_image_1 = np.zeros((ROWS_1,COLS_1), np.uint8)#first predictor map 1
predictor_image_2 = np.zeros((ROWS_2,COLS_2), np.uint8) #first predictor map 2

error_image_1 = np.zeros((frame1Rows,frame1Cols), np.uint8)#first error map 1
error_image_2 = np.zeros((frame2Rows,frame2Cols), np.uint8) #first error map 2


###### LOOP #######
### loop params initilization
weight=0.0
currentWeight=0.0
prev_i=-1
prev_j=-1
prev_k=-1
prev_l=-1
newFrame=False

while(cap1.isOpened() & cap2.isOpened()):
    ret1, frame1 = cap1.read()
    ret2, frame2 = cap2.read()
    newFrame=True
    
    # note the changed axis in opencv
    frame1_reduced  = cv2.resize(frame1,(COLS_1, ROWS_1), interpolation = cv2.INTER_NEAREST)
    frame2_reduced  = cv2.resize(frame2,(COLS_2, ROWS_2), interpolation = cv2.INTER_NEAREST)
    
        
    image_1_t_0 = cv2.cvtColor(frame1_reduced, cv2.COLOR_BGR2GRAY)
    image_2_t_0 = cv2.cvtColor(frame2_reduced, cv2.COLOR_BGR2GRAY)

    # update weights

    for key, value in data.items():
        chainStr= key.split()
        i=int(chainStr[0])  # X_1
        j=int(chainStr[1])  # Y_1
        k=int(chainStr[2])  # X_2
        l=int(chainStr[3])  # Y_2

        # find row in DB and change weight value
        currentWeight = value 


        #if no variation in any of the images, we cannot predict relation
        #so only decay affects output. Similar to losing confidence in 
        #relation (prediction)
       
       # we only make calculation of variation if something has changed
       # either a new frame, or the indexes
        if(i!=prev_i or j!=prev_j or newFrame==True):
            Var_V1 = np.abs(image_1_t_0.item(i,j)-image_1_t_1.item(i,j))

        if(Var_V1==0):
            weight = limit(currentWeight - beta)
        else:
            if(k!=prev_k or l!=prev_l or newFrame==True):
                Var_V2 = np.abs(image_2_t_0.item(k,l)-image_2_t_1.item(k,l))            
            if(Var_V2==0):
                weight = limit(currentWeight - beta)
            else:
                weight = limit(currentWeight + (alpha * Var_V1 * Var_V2 / 255.0) - beta)

        #assign new weight to cell in DB
        data[key]=weight

        ## take advantadge of loop to update maps
        currPix1 = predictor_image_1.item(i,j)
        currPix2 = predictor_image_2.item(k,l)
        predictor_image_1.itemset( (i,j), currPix1 + image_2_t_0.item(k,l)*weight )
        predictor_image_2.itemset( (k,l), currPix2 + image_1_t_0.item(i,j)*weight )
        
        #update indexes
        prev_i=i
        prev_j=j
        prev_k=k
        prev_l=l
        newFrame=False
        
   #update previous image
    image_1_t_1 = image_1_t_0.copy()
    image_2_t_1 = image_2_t_0.copy()
#########################################################
#####   END LOOP   #####################
    
    #### PREDICTOR MAPS ######
    # original size
#    big_predictor_image_1 = cv2.resize(predictor_image_1,(frame1Cols, frame1Rows), interpolation = cv2.INTER_NEAREST)
    #big_predictor_image_2 = cv2.resize(predictor_image_2,(frame2Cols, frame2Rows), interpolation = cv2.INTER_NEAREST)

    # smaller size
    big_predictor_image_1 = cv2.resize(predictor_image_1,(200, 200), interpolation = cv2.INTER_NEAREST)
  #  big_predictor_image_2 = cv2.resize(predictor_image_2,(200, 200), interpolation = cv2.INTER_NEAREST)

    #### SHOW PREDICTOR IMAGES ######
    cv2.imshow('Predictor 1',big_predictor_image_1)
  #  cv2.imshow('Predictor 2',big_predictor_image_2)

    #### SHOW ORIGINAL IMAGES ######
    cv2.imshow('Frame 1', frame1)
   # cv2.imshow('Frame 2', frame2)
    
    #### ERROR MAPS ######
#    resized_original_1 = cv2.resize(image_1_t_0, (frame1Cols,frame1Rows), interpolation = cv2.INTER_NEAREST)
#    error_image_1 = abs( big_predictor_image_1 - resized_original_1 )
#    
#    resized_original_2 = cv2.resize(image_2_t_0, (frame2Cols,frame2Rows), interpolation = cv2.INTER_NEAREST)
#    error_image_2 = abs( big_predictor_image_2 - resized_original_2 )
    #### SHOW ERROR IMAGES ######
#    cv2.imshow('Error 1', error_image_1)
#    cv2.imshow('Error 2', error_image_2)


    if cv2.waitKey(1) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        break
    
    
