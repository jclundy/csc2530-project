import numpy as np
import argparse
import cv2 as cv2
import matplotlib.pyplot as plt
from PIL import Image

import os

image_size = (1920, 1080) # width, height
calibration_file = "calibration.npz"

calibrationParams = np.load(calibration_file)
mtx = calibrationParams['mtx']
dist = calibrationParams['dist']

w = image_size[0]
h = image_size[1]

testNumber = input("input test folder number: ")

base_folder = "C:/Users/littl/OneDrive - University of Toronto/Winter 2025/CSC2530/Project/datasets/scans/laser sweep/laserSweepDistanceTests/laserSweep"
base_folder = base_folder + str(testNumber)

detectionFolder = "dot_detection_output"
outputFolder= os.path.join(base_folder, detectionFolder) 

pose_file = os.path.join(base_folder, "pose.csv")
laser_dots_file = os.path.join(outputFolder, "dots.csv")

poseVals = np.loadtxt(pose_file,
				delimiter=",", dtype=int)
laserDots = np.loadtxt(laser_dots_file,
				delimiter=",", dtype=int)

print("poseVals shape = ", poseVals.shape)
print("laserDots shape = ", laserDots.shape)

laserDots = laserDots[:,0:2]

poseLength = poseVals.shape[0]
dotsLength = laserDots.shape[0]

laserAngles = poseVals[:,1]
baseline = 19.2

M_new, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w,h), 1, (w,h))

cx = M_new[0][2]
cy = M_new[1][2]
fx = M_new[0][0]
fy = M_new[1][1]

laserDotsUndistorted = cv2.undistortPoints(laserDots.astype(np.float64), mtx, dist, None, M_new)

laserDotsUndistorted = np.reshape(laserDotsUndistorted, (-1,2))

"""
Columns
0 - test number
1 - alpha
2 - beta
3 - R
4 - X
5 - Y
6 - Z
"""

outputValues = np.ndarray((dotsLength, 8))

for i in range(0, dotsLength):

    px = laserDotsUndistorted[i, 0]
    py = laserDotsUndistorted[i, 1]

    alpha = np.atan2((px-cx),fx)
    beta = np.atan2((py-cy),fy)

    theta2 = np.pi/2 + alpha
    theta1 = laserAngles[i] * np.pi / 180
    theta3 = np.pi - theta2 - theta1
    
    # distance camera to point
    R =  baseline / np.sin(theta3) * np.sin(theta1)

    Z = R * np.cos(alpha)
    X = R * np.sin(alpha)   
    Y = R * np.tan(beta)

    outputValues[i][0] = i
    outputValues[i][1] = theta1
    outputValues[i][2] = alpha
    outputValues[i][3] = beta
    outputValues[i][4] = R
    outputValues[i][5] = X
    outputValues[i][6] = Y
    outputValues[i][7] = Z

outputFile = os.path.join(outputFolder, 'triangulation.csv')

np.savetxt(outputFile, outputValues, delimiter=',')