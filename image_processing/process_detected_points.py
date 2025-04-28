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

# print("creating output file file")

# outputfile = "triangulation.csv"
# logPath = os.path.join(outputFolder, outputfile)
# logFile = open(logPath, "a")

# for i in range(0,numCaptures, skipStep):
#     pass

# logFile.close()