The .csv files of this directory contain logs of the movements of the centroids of two objects: green, red. Recorded using a version of https://github.com/roboticslab-uc3m/teo-head/blob/master/share/cv1/scripts/cv1.xml

The data delimiter used is the space character (' '), and decimals are separated by the point character ('.'). The data is set in the following order, in plain text and no specific header:

- Timestamp [s]
- x1 (X coordinate of the position of the centroid of green object [m])
- y1 (Y coordinate of the position of the centroid of green object [m])
- z1 (Z coordinate of the position of the centroid of green object [m])
- x2 (X coordinate of the position of the centroid of red object [m])
- y2 (Y coordinate of the position of the centroid of red object [m])
- z2 (Z coordinate of the position of the centroid of red object [m])
- x1-x2
- y1-y2
- z1-z2
- fabs(x1-x2)
- fabs(y1-y2)
- fabs(z1-z2)
- sqrt( pow((x1-x2),2) + pow((y1-y2),2) + pow((z1-z2),2) )

