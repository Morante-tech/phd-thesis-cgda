# -*- coding: utf-8 -*-
"""
Created on Wed Apr 15 12:13:32 2015

@author: smorante
"""

import numpy as np
from itertools import product
import cv2
import fileinput
import bz2
import os

class Network:

    def __init__(self):
        self.alpha_param = None
        self.lambda_param = None
        self.rows = None
        self.cols = None
        self.input_rows = None
        self.input_cols = None
        self.output_rows = None
        self.output_cols= None
        self.weight_matrix = None
        self.block_sum_weights = None
        self.predicted_output_matrix = None


    def create(self, input_rows, input_cols, output_rows, output_cols, alpha_param, lambda_param):
        self.alpha_param = alpha_param
        self.lambda_param = lambda_param
        self.input_rows = input_rows
        self.input_cols = input_cols
        self.output_rows = output_rows
        self.output_cols = output_cols
        
        self.rows = self.input_rows * self.output_rows
        self.cols = self.input_cols * self.output_cols 
        self.block_sum_weights = np.zeros((self.output_rows, self.output_cols), np.float32)
        self.predicted_output_matrix = np.zeros((self.output_rows, self.output_cols), np.float32) 
        
        self.weight_matrix = np.zeros((self.rows, self.cols), np.float32)
        np.ascontiguousarray(self.weight_matrix)

           
    def create_from_file(self, filename, input_rows, input_cols, output_rows, 
                         output_cols, alpha_param, lambda_param, compressed = True):
        self.alpha_param = alpha_param
        self.lambda_param = lambda_param
        self.input_rows = input_rows
        self.input_cols = input_cols
        self.output_rows = output_rows
        self.output_cols = output_cols
        
        self.rows = self.input_rows * self.output_rows
        self.cols = self.input_cols * self.output_cols             
        self.block_sum_weights = np.zeros((self.output_rows, self.output_cols), np.float32)
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
        
        self.weight_matrix = np.load(filename).astype(np.float32)  
        np.ascontiguousarray(self.weight_matrix)   


    def train(self, input_matrix, output_matrix):
        for (i,j) in product(range(self.input_rows), range(self.input_cols)):
       
            # find submatrix in DB and change currentweight value
            block_matrix = self.weight_matrix[(self.output_rows * i):(self.output_rows * (i+1)) ,
                                              (self.output_cols * j):(self.output_cols * (j+1))]

            #if no variation in any of the images, we cannot predict relation
            #Similar to losing confidence in relation
        
            #the elements that add value to the weights
            elem1  = self.alpha_param * input_matrix.item(i,j) * output_matrix
            elem2 = cv2.add(block_matrix, elem1)
            
            #the elements that subtract value to the weights
            elem3 = cv2.absdiff(input_matrix.item(i,j), output_matrix)
            elem4 =  np.square(elem3) * self.lambda_param
            
            #Subtraction of both elems
            elem5 = np.subtract(elem2,elem4)
            
            # limiting weights between 0 and 1
            new_block_matrix = np.clip(elem5, 0, 1)
            
            #assign new weight to cell in DB
            self.weight_matrix[(self.output_rows * i):(self.output_rows * (i+1)) ,
                              (self.output_cols * j):(self.output_cols * (j+1))] = new_block_matrix
            


    def predict(self, input_matrix, max_value=1):
        self.block_sum_weights=0

        for (i,j) in product(range(self.input_rows), range(self.input_cols)):
            # find submatrix in DB
            block_matrix = self.weight_matrix[(self.output_rows * i):(self.output_rows * (i+1)) ,
                                              (self.output_cols * j):(self.output_cols * (j+1))]
        
            # update block_sum_weights    
            self.block_sum_weights= cv2.add(self.block_sum_weights, block_matrix)
            
            # multiply            
            weighted_input_matrix = np.multiply(input_matrix.item(i,j), block_matrix)
            self.predicted_output_matrix = cv2.add(self.predicted_output_matrix , weighted_input_matrix)
            
        ######
        # avoid nan when dividing by zero
        self.predicted_output_matrix  = np.nan_to_num(self.predicted_output_matrix )

        # normalize    
        self.predicted_output_matrix  = np.divide(self.predicted_output_matrix , self.block_sum_weights)
        
        if max_value != None:
            self.predicted_output_matrix = np.clip(self.predicted_output_matrix, 0, max_value)               
        
        return self.predicted_output_matrix
        
    def save_weights_to_file(self, filename, compress=True):
        # save weights matrix
        np.save(filename, self.weight_matrix)            
    
        if compress == True:
            # comprese and delete uncompressed file
            output = bz2.BZ2File(filename + ".bz2", "wb")
             
            for line in fileinput.input(filename):
                    output.write(line)
            output.close()
        
            # remove decompressed file
            os.remove(filename)          
        
    def compute_mse(self, output_matrix, predicted_output_matrix):
        mse_temp_1 = cv2.absdiff(predicted_output_matrix, output_matrix)       
        mse_temp_2 = np.square(mse_temp_1) / (self.output_rows * self.output_cols)
        
        return np.float32( sum( np.array(mse_temp_2).flatten() ) )
        