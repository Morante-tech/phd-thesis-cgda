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

##### CAMS PARAMS #####
#from webcam
# tatup video
#cap1 = cv2.VideoCapture("../../feed/videos/tatup.mp4")
#cap2 = cv2.VideoCapture("../../feed/videos/tatup.mp4")

#synthetic
#cap1 = cv2.VideoCapture("../../feed/videos/synthetic2.ogg")
#cap2 = cv2.VideoCapture("../../feed/videos/synthetic2.ogg")

#from webcam
cap1 = cv2.VideoCapture(0)
cap2 = cv2.VideoCapture(1)
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

##### PARAMETERS ###########
ROWS_1 = int(40) 
''' 
image 1 rows in reduced image to feed the NN with
'''
COLS_1 = int(ROWS_1 * frame1Cols / frame1Rows) 
''' 
image 1 cols in reduced image to feed the NN with
'''
ROWS_2 = int(40)
''' 
image 2 rows in reduced image to feed the NN with
'''
COLS_2 = int(ROWS_2 * frame2Cols / frame2Rows)
''' 
image 2 cols in reduced image to feed the NN with
'''

ALPHA = float(0.3) 
'''
The learning rate is used to determine how aggressive training should be for 
some of the training algorithms (FANN_TRAIN_INCREMENTAL, FANN_TRAIN_BATCH, 
FANN_TRAIN_QUICKPROP).  Do however note that it is not used in FANN_TRAIN_RPROP.
'''

MOMENTUM = float(0.0)
'''
Get the learning momentum.
The learning momentum can be used to speed up FANN_TRAIN_INCREMENTAL training.  
A too high momentum will however not benefit training.  Setting momentum to 0 
will be the same as not using the momentum parameter.  The recommended value 
of this parameter is between 0.0 and 1.0.
The default momentum is 0.
'''

HIDDEN = False
'''
Select if a hidden layer is used or not. Default size = same as input layer
'''

TRAINING_ALGORITHM   = _libfann.TRAIN_INCREMENTAL
'''
TRAIN_INCREMENTAL	Standard backpropagation algorithm, 
where the weights are updated after each training pattern.  
This means that the weights are updated many times during a single epoch.  
For this reason some problems, will train very fast with this algorithm, 
while other more advanced problems will not train very well.

TRAIN_BATCH	Standard backpropagation algorithm, where the weights are 
updated after calculating the mean square error for the whole training set.  
This means that the weights are only updated once during a epoch.  For this 
reason some problems, will train slower with this algorithm.  But since the 
mean square error is calculated more correctly than in incremental training,
some problems will reach a better solutions with this algorithm.

TRAIN_RPROP	A more advanced batch training algorithm which achieves good 
results for many problems.  The RPROP training algorithm is adaptive, and does 
therefore not use the learning_rate.  Some other parameters can however be set 
to change the way the RPROP algorithm works, but it is only recommended for 
users with insight in how the RPROP training algorithm works.  The RPROP 
training algorithm is described by [Riedmiller and Braun, 1993], but the actual 
learning algorithm used here is the iRPROP- training algorithm which is 
described by [Igel and Husken, 2000] which is an variety of the standard RPROP 
training algorithm.

TRAIN_QUICKPROP	A more advanced batch training algorithm which achieves 
good results for many problems.  The quickprop training algorithm uses the 
learning_rate parameter along with other more advanced parameters, but it is 
only recommended to change these advanced parameters, for users with insight 
in how the quickprop training algorithm works.  The quickprop training 
algorithm is described by [Fahlman, 1988].
'''

TRAIN_ERROR_FUNCTION = _libfann.ERRORFUNC_TANH
'''
ERRORFUNC_LINEAR	Standard linear error function.
ERRORFUNC_TANH	Tanh error function, usually better but can require a 
lower learning rate.  This error function agressively targets outputs that 
differ much from the desired, while not targetting outputs that only differ 
a little that much.  This activation function is not recommended for cascade 
training and incremental training.
'''
TRAIN_STOP_FUNCTION  =_libfann.STOPFUNC_MSE
'''
STOPFUNC_MSE	Stop criteria is Mean Square Error (MSE) value.

STOPFUNC_BIT	Stop criteria is number of bits that fail.  The number 
of bits; means the number of output neurons which differ more than the bit 
fail limit (see fann_get_bit_fail_limit, fann_set_bit_fail_limit).  The bits 
are counted in all of the training data, so this number can be higher than the 
number of training data.
'''

ACTIVATION_FUNCTION_HIDDEN =_libfann.SIGMOID
ACTIVATION_FUNCTION_OUTPUT = _libfann.SIGMOID
'''
The functions are described with functions where
x is the input to the activation function,
y is the output,
s is the steepness and
d is the derivation.

LINEAR	Linear activation function.
span: -inf < y < inf
y = x*s, d = 1*s
Can NOT be used in fixed point.

THRESHOLD	Threshold activation function.
x < 0 -> y = 0, x >= 0 -> y = 1
Can NOT be used during training.

THRESHOLD_SYMMETRIC	Threshold activation function.
x < 0 -> y = 0, x >= 0 -> y = 1
Can NOT be used during training.

SIGMOID	Sigmoid activation function.
One of the most used activation functions.
span: 0 < y < 1
y = 1/(1 + exp(-2*s*x))
d = 2*s*y*(1 - y)

-> SIGMOID_STEPWISE	Stepwise linear approximation to sigmoid.
Faster than sigmoid but a bit less precise.

SIGMOID_SYMMETRIC
Symmetric sigmoid activation function, aka. tanh.
One of the most used activation functions.
span: -1 < y < 1
y = tanh(s*x) = 2/(1 + exp(-2*s*x)) - 1
d = s*(1-(y*y))

GAUSSIAN	Gaussian activation function.
0 when x = -inf, 1 when x = 0 and 0 when x = inf
span: 0 < y < 1
y = exp(-x*s*x*s)
d = -2*x*s*y*s

GAUSSIAN_SYMMETRIC	Symmetric gaussian activation function.
-1 when x = -inf, 1 when x = 0 and 0 when x = inf
span: -1 < y < 1
y = exp(-x*s*x*s)*2-1
d = -2*x*s*(y+1)*s

ELLIOT	Fast (sigmoid like) activation function defined by David Elliott
span: 0 < y < 1
y = ((x*s) / 2) / (1 + |x*s|) + 0.5
d = s*1/(2*(1+|x*s|)*(1+|x*s|))

ELLIOT_SYMMETRIC	Fast (symmetric sigmoid like) activation function defined by David Elliott
span: -1 < y < 1
y = (x*s) / (1 + |x*s|)
d = s*1/((1+|x*s|)*(1+|x*s|))

LINEAR_PIECE	Bounded linear activation function.
span: 0 <= y <= 1
y = x*s, d = 1*s

LINEAR_PIECE_SYMMETRIC	Bounded linear activation function.
span: -1 <= y <= 1
y = x*s, d = 1*s

SIN_SYMMETRIC	Periodical sinus activation function.
span: -1 <= y <= 1
y = sin(x*s)
d = s*cos(x*s)

COS_SYMMETRIC	Periodical cosinus activation function.
span: -1 <= y <= 1
y = cos(x*s)
d = s*-sin(x*s)

SIN	Periodical sinus activation function.
span: 0 <= y <= 1
y = sin(x*s)/2+0.5
d = s*cos(x*s)/2

COS	Periodical cosinus activation function.
span: 0 <= y <= 1
y = cos(x*s)/2+0.5
d = s*-sin(x*s)/2
'''

MVMNT_THRES = 10
'''
Movement is detected by pixel. If no movement in the image, its "variation image"
value  is zero. This threshold is used to avoid training the NN with static images,
that is, images were there is no movement. This params is compared with the sum
os all the values of all pixel in each "variation image". Pixel values are
normalize 0-1.

'''

FIX_WEIGHTS_MATRIX = False
'''
This param is used to fix the NN in a specific moment, and dont train it more
'''

MS_TO_WAIT = int(1)
'''
ms to wait for a key in opencv
'''

ACTUAL_IMAGES = True
'''
it determines wheter to predict variations or images
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
############################

#########  NN ############
# setting
ann = libfann.neural_net()
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
################################

## Some neccesary initialization
image_1_t_0  =  np.zeros((ROWS_1, COLS_1), np.uint8) # image 1 previous time
image_2_t_0  =  np.zeros((ROWS_2, COLS_2), np.uint8) # image 2 previous time
image_1_t_1  =  np.zeros((ROWS_1, COLS_1), np.uint8) # image 1 previous time
image_2_t_1  =  np.zeros((ROWS_2, COLS_2), np.uint8) # image 2 previous time
error_image = np.zeros((ROWS_2,COLS_2), np.uint8) # first error map 2

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
    frame1_reduced  = cv2.resize(frame1,(COLS_1, ROWS_1), interpolation = INTERPOLATION_TYPE)
    frame2_reduced  = cv2.resize(frame2,(COLS_2, ROWS_2), interpolation = INTERPOLATION_TYPE)
    
    image_1_t_0 = cv2.cvtColor(frame1_reduced, cv2.COLOR_BGR2GRAY)
    image_2_t_0 = cv2.cvtColor(frame2_reduced, cv2.COLOR_BGR2GRAY)

    # variation image
    var_img1 = cv2.absdiff(image_1_t_0, image_1_t_1)
    var_img2 = cv2.absdiff(image_2_t_0, image_2_t_1)

    
    if ACTUAL_IMAGES == True:
        img1 = np.array(image_1_t_0).flatten().astype(np.float32) / 255.0 # normalize 0-1 for NN
        img2 = np.array(image_2_t_0).flatten().astype(np.float32) / 255.0 # normalize 0-1 for NN

        #calculating total change in pixels
        total_change_img1 = int(sum(np.array(var_img1).flatten().astype(np.float32) / 255.0))
        total_change_img2 = int(sum(np.array(var_img2).flatten().astype(np.float32) / 255.0))

    else:
        img1 = np.array(var_img1).flatten().astype(np.float32) / 255.0 # normalize 0-1 for NN
        img2 = np.array(var_img2).flatten().astype(np.float32) / 255.0 # normalize 0-1 for NN
        
        #calculating total change in pixels
        total_change_img1 = int(sum(img1))
        total_change_img2 = int(sum(img2))
    
  #  print "[INFO] Sum movement 1: ", total_change_img1
  #  print "[INFO] Sum movement 2: ", total_change_img2, "\n"
    
    # train only if enough movement has ocurred
    if FIX_WEIGHTS_MATRIX == False and total_change_img1 > MVMNT_THRES and total_change_img2 > MVMNT_THRES:    
        ann.train(img1, img2)  #train 1 sample (incremental)
   
   # print "[INFO] MSE: ", ann.get_MSE()

    ## PREDICTING SAMPLE
    predictor_image_2_list = ann.run(img1)
    
    ## UPDATE PREVIOUS IMAGES
    image_1_t_1 = image_1_t_0
    image_2_t_1 = image_2_t_0

###########################################
########### VISUALIZATION #################    
###########################################

    #### PREDICTOR MAPS ######
    predictor_image_2 = 255* np.array(predictor_image_2_list).reshape((ROWS_2, COLS_2))   
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
        cv2.imshow('Frame 1', var_img1)
        cv2.imshow('Frame 2', var_img2)    

    #### ERROR MAPS ###### 
    if ACTUAL_IMAGES == True:
        error_image = cv2.absdiff(adaptTypePredictor, image_2_t_0)
    else:
        error_image = cv2.absdiff(adaptTypePredictor, var_img2)

    cv2.namedWindow('Error', cv2.WINDOW_NORMAL)         
    cv2.imshow('Error', error_image)

    #### Keys ###
    k = cv2.waitKey(MS_TO_WAIT) & 0xFF # not use AND (logic), use & (bitwise)
    if k == ord('f'):
        FIX_WEIGHTS_MATRIX = True        
        print '[INFO] WeightsMatrix Fixed'

    if k == ord('q'):
        break
#########################################################
#####################   END LOOP   #####################

cap1.release()
cap2.release()
cv2.destroyAllWindows()