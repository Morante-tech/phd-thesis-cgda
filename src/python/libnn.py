# -*- coding: utf-8 -*-
"""
Created on Wed Apr 15 12:13:32 2015

@author: smorante
"""

import numpy as np
import cv2
import fileinput
import bz2
import os

from fann2 import libfann
from fann2 import _libfann

class NeuralNetwork:

    def __init__(self):
        self.ann = libfann.neural_net()
        self.alpha_param = None
        self.momentum_param = None
        self.activation_function_hidden = None
        self.training_algorithm = None
        self.train_error_function = None      
        self.train_stop_function = None
        self.activation_function_output = None
        
        self.rows = None
        self.cols = None
        self.input_rows = None
        self.input_cols = None
        self.output_rows = None
        self.output_cols= None
        self.predicted_output_matrix = None


    def create(self, input_rows, input_cols, output_rows, output_cols, alpha_param, 
               momentum_param, activation_function_hidden, training_algorithm, 
               train_error_function, train_stop_function, activation_function_output):
                   
        self.alpha_param = alpha_param
        self.momentum_param = momentum_param
        self.activation_function_hidden = activation_function_hidden
        self.training_algorithm = training_algorithm
        self.train_error_function = train_error_function
        self.train_stop_function = train_stop_function
        self.activation_function_output = activation_function_output      
        
        self.input_rows = input_rows
        self.input_cols = input_cols
        self.output_rows = output_rows
        self.output_cols = output_cols
        
        self.rows = self.input_rows * self.output_rows
        self.cols = self.input_cols * self.output_cols 
        self.predicted_output_matrix = np.zeros((self.output_rows, self.output_cols), np.float32) 

#####################
        self.ann.create_standard_array([self.input_rows * self.input_cols ,
                                        self.input_rows * self.input_cols, 
                                        self.output_rows * self.output_cols])
        self.ann.set_activation_function_hidden(activation_function_hidden)
        self.ann.set_learning_rate(alpha_param)
        self.ann.set_learning_momentum(momentum_param)
        self.ann.set_training_algorithm(training_algorithm)
        self.ann.set_train_error_function(train_error_function)
        self.ann.set_train_stop_function(train_stop_function)
        self.ann.set_activation_function_output(activation_function_output)

           
    def create_from_file(self, filename, input_rows, input_cols, output_rows, 
                         output_cols, alpha_param, momentum_param, 
                         activation_function_hidden, training_algorithm, 
                         train_error_function, train_stop_function, 
                         activation_function_output, compressed = True):
                             
        self.alpha_param = alpha_param
        self.momentum_param = momentum_param
        self.activation_function_hidden = activation_function_hidden
        self.training_algorithm = training_algorithm
        self.train_error_function = train_error_function
        self.train_stop_function = train_stop_function
        self.activation_function_output = activation_function_output      
        
        self.input_rows = input_rows
        self.input_cols = input_cols
        self.output_rows = output_rows
        self.output_cols = output_cols
        
        self.rows = self.input_rows * self.output_rows
        self.cols = self.input_cols * self.output_cols 
        self.predicted_output_matrix = np.zeros((self.output_rows, self.output_cols), np.float32) 

        if compressed == True:
            input_file = bz2.BZ2File(filename, "rb")
            try:
                filename = filename.replace(".bz2", "")
                text_file = open(filename, "w")
                text_file.write(input_file.read())
            
            finally:
                input_file.close()
                text_file.close()                
        
        self.ann.create_from_file(filename)


    def train(self, input_matrix, output_matrix):
        self.ann.train(input_matrix, output_matrix)


    def predict(self, input_matrix, max_value=None):
         self.predicted_output_matrix = self.ann.run(input_matrix)       
         return self.predicted_output_matrix

        
    def save_weights_to_file(self, filename, compress=True):
        # save weights matrix
        self.ann.save(filename)        
    
        if compress == True:
            # comprese and delete uncompressed file
            output = bz2.BZ2File(filename + ".bz2", "wb")
             
            for line in fileinput.input(filename):
                    output.write(line)
            output.close()
        
            # remove decompressed file
            os.remove(filename)          
        
    def compute_mse(self, output_matrix, predicted_output_matrix):
        mse_temp_1 = cv2.absdiff(output_matrix.flatten(), 
                                 np.array(predicted_output_matrix).astype(np.float32))
        mse_temp_2 = np.square(mse_temp_1) / (self.output_rows * self.output_cols)
        return np.float32( sum( np.array(mse_temp_2).flatten() ) )