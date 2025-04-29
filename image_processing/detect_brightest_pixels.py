import numpy as np
import argparse
import cv2 as cv2
import matplotlib.pyplot as plt
from PIL import Image

import os


skipStep = 1

image_size = (1920, 1080) # width, height
calibration_file = "calibration.npz"
test_image_file = ""


calibrationParams = np.load(calibration_file)
mtx = calibrationParams['mtx']
dist = calibrationParams['dist']

w = image_size[0]
h = image_size[1]

base_folder = "C:/Users/littl/OneDrive - University of Toronto/Winter 2025/CSC2530/Project/datasets/scans/camera sweep/bathroom_new_a/"

image_folder = os.path.join(base_folder, "images")

laserOffFolder = os.path.join(image_folder, "laserOff")

laserOffImageBaseName = "capture_"
# laserOnDirName = "laserOn"
# laserOnImageBaseName = "laser_"

searchBoxMinX = 1050
searchBoxMinY = 600
searchBoxMaxX = 1350
searchBoxMaxY = 700

# searchBoxMinX = 0
# searchBoxMinY = 0
# searchBoxMaxX = w
# searchBoxMaxY = h

laserOnDirName =  "laserLowExp"
laserOnImageBaseName = "laser_low_exp_"

laserOnFolder = os.path.join(image_folder, laserOnDirName)

numCaptures = len(os.listdir(laserOnFolder))

outputFolder = os.path.join(base_folder, "dot_detection_output", laserOnDirName)

if not os.path.exists(outputFolder):
    os.makedirs(outputFolder)

# beta = 
newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w,h), 1, (w,h))

redLowerLimit = (0,100,100) # (10,255,255)
redUpperLimit = (179,255,255) # (160,100,100) # (179,255,255)

figSize = (9,6)

prevLaserLocation = (1250, 600)

# searchBoxW = 200
# searchBoxH = 200
blur_radius = 5
annotation_radius = 25


searchBoxMinX = int(searchBoxMinX)
searchBoxMinY = int(searchBoxMinY)
searchBoxMaxX = int(searchBoxMaxX)
searchBoxMaxY = int(searchBoxMaxY)

print("creating log file")
logPath = os.path.join(outputFolder, laserOnImageBaseName + "log.csv")
logFile = open(logPath, "a")

for i in range(0,numCaptures, skipStep):
    # print("Capture: ", str(i))

    laserOffImg = laserOffImageBaseName + str(i) +".png"
    laserOffImgFile = os.path.join(laserOffFolder, laserOffImg)

    laserOnImg = laserOnImageBaseName + str(i) +".png"
    laserOnImgFile = os.path.join(laserOnFolder, laserOnImg)
    
    
    img = cv2.imread(laserOffImgFile)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR )
 
    laserImg = cv2.imread(laserOnImgFile)
    laserImg = cv2.cvtColor(laserImg, cv2.COLOR_RGB2BGR )
 
    imgGrey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    laserImgGrey = cv2.cvtColor(laserImg, cv2.COLOR_BGR2GRAY)
    # (score, diff) = compare_ssim(imgGrey, laserImgGrey, full=True)
    # diff = (diff * 255).astype("uint8")
    # print("SSIM: {}".format(score))

    
    # print(searchBoxMinX, searchBoxMaxX, searchBoxMinY, searchBoxMaxY)

    # searchRegionMask = np.zeros(laserImgGrey.shape, dtype="uint8")
    # # print(mask.shape)
    # searchRegionMask[searchBoxMinY:searchBoxMaxY, searchBoxMinX:searchBoxMaxX] = 1

    # print(np.max(searchRegionMask))
    
    # outputImgName = str(i) + "_searchRegionMask.png"
    # 
    # cv2.imwrite(outputImageFile,searchRegionMask)

    laserGrayBlurred = cv2.GaussianBlur(laserImgGrey, (blur_radius, blur_radius), 0)

    # searchRegionMasked = cv2.bitwise_and(laserGrayBlurred, searchRegionMask)
    # print(laserGrayBlurred.shape)
    searchRegionMasked = np.zeros(laserGrayBlurred.shape)
    searchRegionMasked[searchBoxMinY:searchBoxMaxY, searchBoxMinX:searchBoxMaxX] = laserGrayBlurred[searchBoxMinY:searchBoxMaxY, searchBoxMinX:searchBoxMaxX]

    # th3 = cv2.adaptiveThreshold(searchRegionMasked,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11,2)

    (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(searchRegionMasked)

    line = str(maxLoc[0]) + ", " + str(maxLoc[1])
    logFile.write(line)
    logFile.write("\n")

    # print(maxLoc)
    prevLaserLocation = maxLoc
    
    annotated = laserImg.copy()
    cv2.circle(annotated, maxLoc, annotation_radius, (0, 0, 255), 2)
    cv2.rectangle(annotated, (searchBoxMinX, searchBoxMinY), (searchBoxMaxX, searchBoxMaxY),(255, 0, 0),2 )
    
    outputImgName = str(i) + "_annotated.png"
    outputImageFile = os.path.join(outputFolder, outputImgName)
    cv2.imwrite(outputImageFile,annotated)