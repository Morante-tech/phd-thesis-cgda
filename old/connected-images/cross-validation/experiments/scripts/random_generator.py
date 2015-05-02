# -*- coding: utf-8 -*-
"""
Created on Thu Apr  9 14:25:38 2015

@author: smorante
"""

import numpy as np
import cv2
import sys

rows=120 # no small values please!
cols=160

##################################
# Define the codec and create VideoWriter object
out = cv2.VideoWriter('output2.avi',cv2.cv.CV_FOURCC('X','V','I','D'), 20, (cols,rows), isColor=False)
if not out:
    print "Error in creating video writer"
    sys.exit(1)
frame = np.zeros((rows,cols), dtype=np.uint8)

while(True):
    
    cv2.randu(frame, 0, 255)
    out.write(frame)

    cv2.imshow('random 1', frame)
        
    k = cv2.waitKey(5) & 0xFF # dont use AND (logic), use & (bitwise)

    if k == ord('q'):
        break 
        
out.release()
cv2.destroyAllWindows()