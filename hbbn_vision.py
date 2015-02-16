# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import numpy as np
import cv2
import pandas as pd
from scipy.special import expit


#params
ROWS_1 = 3
COLS_1 = 3
ROWS_2 = 2
COLS_2 = 2

alpha = 1
beta =0.01

# create dataframe
#colsNames = ['X_1', 'Y_1', 'X_2', 'Y_2', 'weights']

numberOfRows = ( ROWS_1 * COLS_1 * ROWS_2 * COLS_2 )
#data = pd.DataFrame(index=np.arange(numberOfRows), columns=colsNames, data=0)
data = pd.DataFrame(index=np.arange(numberOfRows), columns=['weights'],data=0.0)

### LOOP ####

# Load an color image in grayscale
big_image_1_t_0 = cv2.imread('uno.jpg',0)
big_image_2_t_0 = cv2.imread('dos.jpg',0)

image_1_t_0  = cv2.resize(big_image_1_t_0,(ROWS_1, COLS_1), interpolation = cv2.INTER_LINEAR)
image_2_t_0  = cv2.resize(big_image_2_t_0,(ROWS_2, COLS_2), interpolation = cv2.INTER_LINEAR)

#temporal
image_1_t_1 = cv2.imread('uno_b.jpg',0)
image_2_t_1 = cv2.imread('dos_b.jpg',0)


indexDB = 0
weight  = 0




for l in range(COLS_2):
    for k in range(ROWS_2):
        for j in range(COLS_1):
            for i in range(ROWS_1):
                Var_V1 = (np.abs(image_1_t_0[i,j]-image_1_t_1[i,j]))/255.0
                Var_V2 = (np.abs(image_2_t_0[k,l]-image_2_t_1[k,l]))/255.0
                weight = expit(weight + alpha * Var_V1 * Var_V2 - beta)
                data['weights'][indexDB]=weight
                indexDB +=1



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



