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
ROWS_1 = 2
COLS_1 = 3
ROWS_2 = 3
COLS_2 = 3

alpha = 1
beta =0.01

# create dataframe
colsNames = ['X_1', 'Y_1', 'X_2', 'Y_2', 'weights']

numberOfRows =  ROWS_1 * COLS_1 * ROWS_2 * COLS_2 
data = pd.DataFrame(index=np.arange(numberOfRows), 
                    columns=colsNames, 
                    data=0)

### LOOP ####

# Load an color image in grayscale
big_image_1_t_0 = cv2.imread('lat.jpg',0)
big_image_2_t_0 = cv2.imread('front.jpg',0)

image_1_t_0  = cv2.resize(big_image_1_t_0,(ROWS_1, COLS_1), interpolation = cv2.INTER_LINEAR)
image_2_t_0  = cv2.resize(big_image_2_t_0,(ROWS_2, COLS_2), interpolation = cv2.INTER_LINEAR)

#temporal
big_image_1_t_1 = cv2.imread('lat_b.jpg',0)
big_image_2_t_1 = cv2.imread('front_b.jpg',0)

image_1_t_1  = cv2.resize(big_image_1_t_1,(ROWS_1, COLS_1), interpolation = cv2.INTER_LINEAR)
image_2_t_1  = cv2.resize(big_image_2_t_1,(ROWS_2, COLS_2), interpolation = cv2.INTER_LINEAR)

##### filling data

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


################################################
######## help

##
#cv2.imshow('uno',image_1_t_0)
#cv2.waitKey(0)
#cv2.destroyAllWindows()


## pure python
#In [144]: df[(df.a < df.b) & (df.b < df.c)]
#Out[144]: 
#          a         b         c
#2  0.276464  0.801872  0.958139
#
## query
#In [145]: df.query('(a < b) & (b < c)')
#Out[145]: 
#          a         b         c
#2  0.276464  0.801872  0.958139



