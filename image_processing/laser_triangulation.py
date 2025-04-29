import numpy as np
import argparse
import cv2
# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", help = "path to the image file")
ap.add_argument("-r", "--radius", type = int,
	help = "radius of Gaussian blur; must be odd")
ap.add_argument("-c", "--calibration", help = "path to calibration file")
args = vars(ap.parse_args())

image_size = (1920, 1080) # width, height

calibration_file = args["calibration"]
if calibration_file is None:
    calibration_file = "calibration.npz"

print("using calibration file at: " + calibration_file)

calibrationParams = np.load(calibration_file)
mtx = calibrationParams['mtx']
dist = calibrationParams['dist']

# SIMPLIFIED METHOD
# - get pixel location in 

alphaX = mtx[0][0]
alphaY = mtx[1][1]

imageWidth = image_size[0]
fovX = np.atan(imageWidth/(2*alphaX))

fovX_deg = fovX * 180/np.pi
print("foVX in degrees: " + str(fovX_deg))

# show image
# pick pixel (user input)
# input radius (user input)

# in openCV draw bounding box

# load calibration
# - show uncalibrated image
# - show rectified image

# get laser angle


