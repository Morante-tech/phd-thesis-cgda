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
import pandas as pd
from scipy.special import expit

#params
ROWS_1 = 10
COLS_1 = 10
ROWS_2 = 10
COLS_2 = 10

alpha = 0.1
beta =0.001

# video

cap1 = cv2.VideoCapture('videos/video.mp4')
cap2 = cv2.VideoCapture('videos/video.mp4')


# create dataframe
numberOfRows =  ROWS_1 * COLS_1 * ROWS_2 * COLS_2 

data = pd.DataFrame(index=np.arange(numberOfRows), 
                    columns=['X_1', 'Y_1', 'X_2', 'Y_2', 'weights'],
                    data=0)
                    
# converting types to save space                    
data[['X_1', 'Y_1', 'X_2', 'Y_2']] = data[['X_1', 'Y_1', 'X_2', 'Y_2']].astype('int32')
data['weights'] = data['weights'].astype('float16')

#### filling initial data
## first column
repetitionsROWS_1 =  COLS_1 * ROWS_2 * COLS_2 
join=[]
for i in range(ROWS_1):
    join = join + [i]*repetitionsROWS_1
data['X_1']=join

## second column
repetitionsCOLS_1 =  repetitionsROWS_1 / COLS_1 
join=[]
for i in range(COLS_1):
        join = join + [i]*repetitionsCOLS_1
join = join*ROWS_1
        
data['Y_1']=join

## third column
repetitionsROWS_2 =  repetitionsCOLS_1 / ROWS_2 
join=[]
for i in range(ROWS_2):
        join = join + [i]*repetitionsROWS_2
join = join*ROWS_1*COLS_1
        
data['X_2']=join

## fourth column
repetitionsCOLS_2 =  repetitionsROWS_2 / COLS_2 
join=[]
for i in range(COLS_2):
        join = join + [i]*repetitionsCOLS_2
join = join*ROWS_1*COLS_1*ROWS_2
        
data['Y_2']=join
join=[]
#######

## some neccesary initialization

image_1_t_1  =  np.zeros((COLS_1, ROWS_1), np.uint8) # image 1 previous time
image_2_t_1  =  np.zeros((COLS_2, ROWS_2), np.uint8) # image 2 previous time
predictor_image_1 = np.zeros((ROWS_1,COLS_1), np.uint8)#first predictor map 1
predictor_image_2 = np.zeros((ROWS_2,COLS_2), np.uint8) #first predictor map 2

###### LOOP #######

while(cap1.isOpened() & cap2.isOpened()):
    ret1, frame1 = cap1.read()
    ret2, frame2 = cap2.read()


    # note the changed axis in opencv
    frame1_reduced  = cv2.resize(frame1,(COLS_1, ROWS_1))
    frame2_reduced  = cv2.resize(frame2,(COLS_2, ROWS_2))
    
    image_1_t_0 = cv2.cvtColor(frame1_reduced, cv2.COLOR_BGR2GRAY)
    image_2_t_0 = cv2.cvtColor(frame2_reduced, cv2.COLOR_BGR2GRAY)

    
    # weights initilization
    weight=0.0
    currentWeight=0.0

    # update weights
    for index, row in data.iterrows():
        i=row['X_1']
        j=row['Y_1']
        k=row['X_2']
        l=row['Y_2']
        
        Var_V1 = (np.abs(image_1_t_0[i,j]-image_1_t_1[i,j]))
        Var_V2 = (np.abs(image_2_t_0[k,l]-image_2_t_1[k,l]))

        # find row in DB and change weight value
        currentWeight = row['weights'] 

        weight = expit(currentWeight + alpha * (Var_V1 * Var_V2) / 255.0 - beta)
        row['weights']=weight
        
        #take advantadge of loop to update maps
        predictor_image_1[i,j] +=  image_2_t_0[k,l]*weight
        predictor_image_2[k,l] +=  image_1_t_0[i,j]*weight

                    
    big_predictor_image_1 = cv2.resize(predictor_image_1,(200, 200), interpolation = cv2.INTER_NEAREST)
    big_predictor_image_2 = cv2.resize(predictor_image_2,(200, 200), interpolation = cv2.INTER_NEAREST)

    image_1_t_1 = image_1_t_0.copy()
    image_2_t_1 = image_2_t_0.copy()

    
    cv2.imshow('frame1',frame1)
    cv2.imshow('frame2',frame2)
    cv2.imshow('Predictor 1',big_predictor_image_1)
    cv2.imshow('Predictor 2',big_predictor_image_2)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        break