# -*- coding: utf-8 -*-
"""
Created on Wed Apr 15 12:13:32 2015

@author: smorante
"""

from fann2 import libfann

class NeuralNetwork:

    def __init__(self):
        self.ann = libfann.neural_net()

#############################################
    def create(self, input_neurons_size, hidden_neurons_size, output_neurons_size,
               alpha_param, momentum_param, training_algorithm, train_error_function,
               train_stop_function, activation_function_hidden, activation_function_output):

        self.input_neurons_size = input_neurons_size
        self.hidden_neurons_size = hidden_neurons_size
        self.output_neurons_size = output_neurons_size

        # setting param
        self.ann.create_standard_array([self.input_neurons_size,
                                        self.hidden_neurons_size,
                                        self.output_neurons_size])
        self.ann.set_activation_function_hidden(activation_function_hidden)
        self.ann.set_learning_rate(alpha_param)
        self.ann.set_learning_momentum(momentum_param)

        self.ann.set_training_algorithm(training_algorithm)
        self.ann.set_train_error_function(train_error_function)
        self.ann.set_train_stop_function(train_stop_function)
        self.ann.set_activation_function_output(activation_function_output)

#############################################
    def train(self, input_array, output_array):
        self.ann.train(input_array, output_array)
        print("[INFO] Mean Square Error: ", self.ann.get_MSE())

#############################################
    def predict(self, input_array):
        return self.ann.run(input_array)
