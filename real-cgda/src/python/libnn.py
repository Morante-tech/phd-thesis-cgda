# -*- coding: utf-8 -*-
"""
Created on Wed Apr 15 12:13:32 2015

@author: smorante
"""

#import numpy as np
import fileinput
import bz2
import os
from fann2 import libfann

class NeuralNetwork:

    def __init__(self):
        self.ann = libfann.neural_net()
  #      self.input_neurons = None
  #      self.hidden_neurons = None
   #     self.output_neurons = None

#############################################
    def create(self, input_neurons, hidden_neurons, output_neurons, alpha_param, 
               momentum_param, training_algorithm, train_error_function, 
               train_stop_function, activation_function_hidden, activation_function_output):
        
        self.input_neurons = input_neurons
        self.hidden_neurons = hidden_neurons
        self.output_neurons = output_neurons
        
        # setting param
        self.ann.create_standard_array([self.input_neurons,
                                        self.hidden_neurons, 
                                        self.output_neurons])
        self.ann.set_activation_function_hidden(activation_function_hidden)
        self.ann.set_learning_rate(alpha_param)
        self.ann.set_learning_momentum(momentum_param)
        
        self.ann.set_training_algorithm(training_algorithm)
        self.ann.set_train_error_function(train_error_function)
        self.ann.set_train_stop_function(train_stop_function)
        self.ann.set_activation_function_output(activation_function_output)

#############################################           
    def create_from_file(self, filename, input_neurons, hidden_neurons, output_neurons, 
                         alpha_param, momentum_param, training_algorithm, train_error_function, 
                         train_stop_function, activation_function_hidden, 
                         activation_function_output, compressed = True):     
        
        self.input_neurons = input_neurons
        self.hidden_neurons = hidden_neurons
        self.output_neurons = output_neurons
        self.ann.create_standard_array([self.input_neurons,
                                        self.hidden_neurons, 
                                        self.output_neurons])
        self.ann.set_learning_rate(alpha_param)
        self.ann.set_learning_momentum(momentum_param)
        
        self.ann.set_training_algorithm(training_algorithm)
        self.ann.set_train_error_function(train_error_function)
        self.ann.set_train_stop_function(train_stop_function)
        self.ann.set_activation_function_hidden(activation_function_hidden)
        self.ann.set_activation_function_output(activation_function_output)
        
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

#############################################
    def train(self, input_array, output_array):
        self.ann.train(input_array, output_array)

#############################################
    def predict(self, input_array):
         predicted_output_array = self.ann.run(input_array) 
         return predicted_output_array

 #############################################       
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
    