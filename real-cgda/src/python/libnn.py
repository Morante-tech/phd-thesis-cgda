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

class NeuralNetwork:

    def __init__(self):
        self.ann = libfann.neural_net()
        self.input_rows = None
        self.input_cols = None
        self.output_rows = None
        self.output_cols= None


    def create(self, input_rows, input_cols, output_rows, output_cols, alpha_param, 
               momentum_param, training_algorithm, train_error_function, 
               train_stop_function, activation_function_hidden, activation_function_output):
        
        self.input_rows = input_rows
        self.input_cols = input_cols
        self.output_rows = output_rows
        self.output_cols = output_cols
        
        # setting param
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
                         training_algorithm, train_error_function, 
                         train_stop_function, activation_function_hidden, 
                         activation_function_output, compressed = True):     
        
        self.input_rows = input_rows
        self.input_cols = input_cols
        self.output_rows = output_rows
        self.output_cols = output_cols
        

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
        self.ann.train(input_matrix.flatten(), output_matrix.flatten())


    def predict(self, input_matrix, max_value=None):
         predicted_output_matrix = self.ann.run(input_matrix.flatten()) 
         return (np.array(predicted_output_matrix).reshape((self.output_rows, self.output_cols))).astype(np.float32)

        
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
        mse_temp_1 = cv2.absdiff(output_matrix.flatten(), predicted_output_matrix.flatten())
        mse_temp_2 = np.square(mse_temp_1) / (self.output_rows * self.output_cols)
        return np.float32( sum( np.array(mse_temp_2).flatten() ) )