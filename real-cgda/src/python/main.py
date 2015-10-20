# -*- coding: utf-8 -*-
"""
Author: Santiago Morante
Robotics Lab. Universidad Carlos III de Madrid
About: This file uses neural network to create an inverse model between the 
feature space (network input) and the joint or cartesian space (network output).
"""

import numpy as np
import libnn
import cv2
import time
import csv
import sys
import os
from fann2 import _libfann


############################
def load_experiment_params(filename):
    #### REPRODUCE EXPERIMENT ####
    experiment_list=[]
    with open(filename, "rb") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            experiment_list.append(row)
    print "[INFO] Experiment raw data: ", experiment_list [1]
    
    input_source = experiment_list [1][0]
    output_source = experiment_list [1][1]
    alpha_param = float(experiment_list [1][2])
    momentum_param = float(experiment_list [1][3])
    training_algorithm = int(experiment_list [1][4])
    train_error_function = int(experiment_list [1][5])
    train_stop_function = int(experiment_list [1][6])
    activation_function_hidden = int(experiment_list [1][7])
    activation_function_output = int(experiment_list [1][8])
    filename_precomputed_weights = experiment_list [1][9]
    
    return (input_source, output_source,alpha_param,momentum_param,training_algorithm,
            train_error_function, train_stop_function, activation_function_hidden,
            activation_function_output, filename_precomputed_weights)

def save_experiment_params(filename, input_source, output_source,alpha_param,momentum_param,training_algorithm,
            train_error_function, train_stop_function, activation_function_hidden,
            activation_function_output, filename_precomputed_weights):
    
    list_params_names = ["input_source", "output_source", "alpha_param", "momentum_param", 
                         "training_algorithm","train_error_function", "train_stop_function",  
                         "activation_function_hidden", "activation_function_output",
                         "filename_precomputed_weights"]
    
    list_params_values = [input_source, output_source,alpha_param,momentum_param,training_algorithm,
                          train_error_function, train_stop_function, activation_function_hidden,
                          activation_function_output, filename_precomputed_weights]    
    
    
    file_params = open(filename, "w")           
    file_params.write(",".join(map(lambda x: str(x), list_params_names)))
    file_params.write("\n")
    file_params.write(",".join(map(lambda x: str(x), list_params_values)))
    file_params.write("\n")
    file_params.close()           


############################################################################
############################### CONFIGURATION ##############################
############################################################################
REPRODUCE_EXPERIMENT = False 
TRAINING = True
EXPERIMENT_PARAMS_FILENAME = ""
SAVE_EXPERIMENT   = False
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
nn = libnn.NeuralNetwork()
 
if REPRODUCE_EXPERIMENT == True:
    #### REPRODUCE EXPERIMENT ####
    #extract params from file
    input_source, output_source,alpha_param,momentum_param,training_algorithm, \
    train_error_function, train_stop_function, activation_function_hidden,  \
    activation_function_output, filename_precomputed_weights = load_experiment_params(EXPERIMENT_PARAMS_FILENAME)

    print "[INFO] Params extracted from file"

     # create network
    nn.create_from_file(input_source, output_source,alpha_param,momentum_param,
                        training_algorithm, train_error_function, train_stop_function, 
                        activation_function_hidden, activation_function_output, 
                        filename_precomputed_weights, compressed = False)

    print "[INFO] Using loaded weight matrix"
    
else:         
    ##### CONFIGURE NEW EXPERIMENT ###########
    input_source = "../../raws/videos/sintel.avi"
    output_source = "../../raws/videos/sintel.avi"

    input_neurons_size = "sacar size de input_source"
    hidden_neurons_size = "lo que queramos"
    output_neurons_size = "sacar size de output_source"
    
    
    input_array= "valor de array en loop"    
    output_array= "valor de array en loop"    

    alpha_param = 0.05
    momentum_param = 0.5
    training_algorithm =   _libfann.TRAIN_INCREMENTAL
    train_error_function = _libfann.ERRORFUNC_TANH
    train_stop_function =  _libfann.STOPFUNC_MSE
    activation_function_hidden =  _libfann.SIGMOID
    activation_function_output =  _libfann.SIGMOID
 #############################################
    
    nn.create(input_neurons_size, hidden_neurons_size, output_neurons_size, alpha_param, \
               momentum_param, training_algorithm, train_error_function, \
               train_stop_function, activation_function_hidden, activation_function_output)

    # Getting info from NN
    print "[INFO] sizes ann: ", nn.ann.get_num_input(), " and ",  nn.ann.get_num_output()
    print "[INFO] total number of neurons: " , nn.ann.get_total_neurons()
    print "[INFO] total number of connections: " , nn.ann.get_total_connections()
    print "[INFO] ann params: ", nn.ann.print_parameters()  
    
############ LOOP ############
while(True):
    
    # train weights
    if REPRODUCE_EXPERIMENT == False and TRAINING == True:
        nn.train(input_array, output_array)
        
        
    # predict weights
    nn.predict(input_array)
    
    ##### GRAB KEY AND EXIT #########
    k = cv2.waitKey(1) & 0xFF # dont use AND (logic), use & (bitwise)
  
    if k == ord('q'):                  
        break
  
    if k == ord('f'):
        fix_weights_matrix = True        
        print "[INFO] WeightsMatrix Fixed"

################  END LOOP  #####################


if SAVE_EXPERIMENT == True:
    print "[INFO] Saving experiment"         

      # save weights matrix
    print "[INFO] Saving weights"
    FILENAME_WEIGHTS = "../../cross-validation/experiments/weights/nn_weights_" \
    + DATE + "_" + TIME +  ".npy"
    nn.save_weights_to_file(FILENAME_WEIGHTS, False)      

    # save params
    print "[INFO] Saving params"
    FILENAME_PARAMS = "../../cross-validation/experiments/params/nn_params_"   \
    + DATE + "_" + TIME  + ".csv"       
    
    list_params_names = ["SOURCE_1", "SOURCE_2", "FILENAME_WEIGHTS", "FILENAME_RESULTS", 
                         "FILENAME_PARAMS","INPUT_ROWS", "INPUT_COLS", "OUTPUT_ROWS", 
                         "OUTPUT_COLS", "ALPHA", "MOMENTUM", "TRAINING_ALGORITHM", 
                         "TRAIN_ERROR_FUNCTION", "TRAIN_STOP_FUNCTION", 
                         "ACTIVATION_FUNCTION_HIDDEN", "ACTIVATION_FUNCTION_OUTPUT", 
                         "ACTUAL_IMAGES", "MOVEMENT_THRESHOLD"]
    
    list_params_values = [SOURCE_1, SOURCE_2, FILENAME_WEIGHTS, FILENAME_RESULTS, 
                         FILENAME_PARAMS, INPUT_ROWS, INPUT_COLS, OUTPUT_ROWS, OUTPUT_COLS, 
                         ALPHA, MOMENTUM, TRAINING_ALGORITHM, 
                         TRAIN_ERROR_FUNCTION, TRAIN_STOP_FUNCTION, 
                         ACTIVATION_FUNCTION_HIDDEN, ACTIVATION_FUNCTION_OUTPUT, 
                         ACTUAL_IMAGES, MVMNT_THRES]
    
    save_params(list_params_names, list_params_values)
 
# cleaning
#if REPRODUCE_EXPERIMENT == True:
#    print "[INFO] Removing decompressed file"
#    temp = FILENAME_PRECOMPUTED_WEIGHTS.replace(".bz2", "")
#    os.remove(FILENAME_PRECOMPUTED_WEIGHTS.replace(".bz2", ""))  
    
print "[INFO] Bye, bye!"