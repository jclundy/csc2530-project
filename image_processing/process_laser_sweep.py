import numpy as np
import argparse
import cv2 as cv2
import matplotlib.pyplot as plt
from PIL import Image

import os

skipStep = 1

image_size = (1920, 1080) # width, height
calibration_file = "calibration.npz"

calibrationParams = np.load(calibration_file)
mtx = calibrationParams['mtx']
dist = calibrationParams['dist']

w = image_size[0]
h = image_size[1]

testNumber = input("input test folder number:　")

base_folder = "C:/Users/littl/OneDrive - University of Toronto/Winter 2025/CSC2530/Project/datasets/scans/laser sweep/laserSweepDistanceTests/laserSweep"
base_folder = base_folder + str(testNumber)

print("base folder: ", base_folder)
image_folder = os.path.join(base_folder, "images")

numCaptures = len(os.listdir(image_folder))
print(numCaptures)

outputFolder = "dot_detection_output"

outputFolder= os.path.join(base_folder, outputFolder) 

if not os.path.exists(outputFolder):
    os.makedirs(outputFolder)

print("creating log file")
logPath = os.path.join(outputFolder, "dots.csv")
logFile = open(logPath, "a")

laserDots = []

blur_radius = 5
annotation_radius = 10


searchBoxMinX = 0
searchBoxMinY = 0
searchBoxMaxX = w
searchBoxMaxY = h

searchBoxMinX = int(searchBoxMinX)
searchBoxMinY = int(searchBoxMinY)
searchBoxMaxX = int(searchBoxMaxX)
searchBoxMaxY = int(searchBoxMaxY)

for i in range(0,numCaptures, skipStep):
    print("Capture: ", str(i))

    laserOnImgName = "capture_" + str(i) +".png"
    laserOnImgFile = os.path.join(image_folder, laserOnImgName)   
 
    laserImg = cv2.imread(laserOnImgFile)
    laserImg = cv2.cvtColor(laserImg, cv2.COLOR_RGB2BGR )
    laserImgGrey = cv2.cvtColor(laserImg, cv2.COLOR_BGR2GRAY)


    laserGrayBlurred = cv2.GaussianBlur(laserImgGrey, (blur_radius, blur_radius), 0)

    searchRegionMasked = np.zeros(laserGrayBlurred.shape)
    searchRegionMasked[searchBoxMinY:searchBoxMaxY, searchBoxMinX:searchBoxMaxX] = laserGrayBlurred[searchBoxMinY:searchBoxMaxY, searchBoxMinX:searchBoxMaxX]
    (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(searchRegionMasked)

    # (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(laserGrayBlurred)

    laserDots.append(maxLoc)

    line = str(maxLoc[0]) + ", " + str(maxLoc[1])
    logFile.write(line)
    logFile.write("\n")

    print(maxLoc)
    prevLaserLocation = maxLoc
    
    annotated = laserImg.copy()
    cv2.circle(annotated, maxLoc, annotation_radius, (0, 0, 255), 2)
    cv2.rectangle(annotated, (searchBoxMinX, searchBoxMinY), (searchBoxMaxX, searchBoxMaxY),(255, 0, 0),2 )
    
    outputImgName = str(i) + "_annotated.png"
    outputImageFile = os.path.join(outputFolder, outputImgName)
    cv2.imwrite(outputImageFile,annotated)

logFile.close()