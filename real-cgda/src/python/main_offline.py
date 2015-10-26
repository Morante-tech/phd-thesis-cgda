# -*- coding: utf-8 -*-
"""
Author: Santiago Morante
Robotics Lab. Universidad Carlos III de Madrid
About: This file uses neural network to create an inverse model between the
feature space (network input) and the joint or cartesian space (network output).
"""

import libnn
from fann2 import _libfann
import pandas as pd
import numpy as np
from sklearn.cross_validation import train_test_split
from sklearn import preprocessing

##########################################################################
############################# PARAMETERS ##############################
##########################################################################
source = "../../data/data.csv"
alpha_param = 0.1
momentum_param = 0.5
test_size_fraction = 0.2
training_algorithm =   _libfann.TRAIN_INCREMENTAL
train_error_function = _libfann.ERRORFUNC_TANH
train_stop_function =  _libfann.STOPFUNC_MSE
activation_function_hidden =  _libfann.SIGMOID
activation_function_output =  _libfann.SIGMOID

############ CONFIGURE NN ###############
raw_data = pd.read_csv(source)

#extract column names
list_column_names = list(raw_data.columns.values)

# convert column names to list, find first OUT column
input_neurons_size = list_column_names.index("OUT")

# output equals total columns - input columns
output_neurons_size = len(list_column_names) - input_neurons_size

# number of hidden neurons equals average between input and output size
hidden_neurons_size = int(np.ceil((input_neurons_size + output_neurons_size) / 2))


###### CREATE AND SET NN #############
nn = libnn.NeuralNetwork()
nn.create(input_neurons_size, hidden_neurons_size, output_neurons_size, alpha_param, \
           momentum_param, training_algorithm, train_error_function, \
           train_stop_function, activation_function_hidden, activation_function_output)

# Getting info from NN
#print "[INFO] ann params: \n", nn.ann.print_parameters()



######### FEATURE SCALING #############

# raw data
raw_input_data = raw_data.ix[:,0:input_neurons_size].copy()
print "[INFO] Raw Input Data: \n", raw_input_data
raw_output_data = raw_data.ix[:,input_neurons_size:len(list_column_names)].copy()
print "[INFO] Raw Output Data: \n", raw_output_data

# scaled data
scaled_input_data = pd.DataFrame(preprocessing.StandardScaler().fit_transform(raw_input_data), columns=raw_input_data.columns)
print "[INFO] Scaled Input Data: \n", pd.DataFrame(scaled_input_data)

#concat
scaled_data = pd.concat([scaled_input_data, raw_output_data], axis=1)
print "[INFO] Scaled Data: \n", scaled_data

############# SETTING SETS ############
train_data, test_data = train_test_split(scaled_data, test_size = test_size_fraction)

####### TRAINING ##########
for index,row in train_data.iterrows():
    # selecting input columns
    input_array  = list(row[0:input_neurons_size])

    # selecting output columns
    output_array = list(row[input_neurons_size:len(list_column_names)])

    # training
    nn.train(input_array, output_array)

###### TESTING ##########
for index,row in test_data.iterrows():
    # selecting input columns
    input_array  = list(row[0:input_neurons_size])

    # predicting
    print nn.predict(input_array)


###########  END LOOP  ############
print "[INFO] Bye, bye!"