from common import *
from threading import Thread
from queue import Queue
import time
import os
import numpy as np

def log_pose(file, step, laser, pan, tilt):
    line = str(step) + ", " + str(laser) + ", " + str(pan) + ", " + str(tilt)
    file.write(line)
    file.write("/n")

def run_command_sequence(params, serial_queue, camera_queue):
    laserStartAngle = params["startAngle"]
    incrementAngle = params["incrementAngle"]
    numSteps = params["numSteps"]
    baseDir = params["baseDir"]
    panAngle = params["panAngle"]
    tiltAngle = params["tiltAngle"]

    laserOnCommand = "a:1\n"
    laserOffCommand = "a:0\n"

    laserAngleCommand = "b:" + str(laserStartAngle) + "\n"
    currentLaserAngle = laserStartAngle
    serial_queue.put(laserAngleCommand)
    time.sleep(2)
    
    panAngleCommand = "c:" + str(panAngle)  + "\n"
    currentPanAngle = panAngle
    serial_queue.put(panAngleCommand)
    time.sleep(2)

    tiltAngleCommand = "c:" + str(tiltAngle)  + "\n"
    currentTiltAngle = tiltAngle
    serial_queue.put(tiltAngleCommand)
    time.sleep(2)

    serial_queue.put(laserOnCommand)

    logPath = baseDir + "/"
    logPath = os.path.join(baseDir, "pose.csv")
    logFile = open(logPath, "a")

    if not os.path.isfile(log_path):
        with open(log_path, "w") as file:
            file.write("User Activity Log\n")
        print("Log file created.")

    for i in range(0,numSteps +1):
        log_pose(logFile, i, currentLaserAngle, currentPanAngle, currentTiltAngle)

        imageFileName = os.path.join(baseDir, "images", "capture_") + str(i) + ".png"
        save_command = ('sn', imageFileName)
        camera_queue.put(save_command)
        time.sleep(0.5)
        currentLaserAngle = np.round(laserStartAngle + i * laserIncrement)
        laserAngleCommand = "b:" + str(currentLaserAngle) + "\n"
        serial_queue.put(laserAngleCommand)
        time.sleep(4)
    # loop - end

    # end of thread
    quit_command = ('q', None)
    serial_queue.put(quit_command)
    camera_queue.put(quit_command)

if __name__ == '__main__':
 
    # User input
    baseDir = input("Enter image folder name")

    if not os.path.exists(baseDir):
        os.makedirs(baseDir)
        print("Log directory created.")

    userInput = input("Enter laser start angle: ")
    while (is_convertible_to_int(userInput) == False):
        print("Invalid numeric input")
        userInput = input("Enter laser start angle: ")
    laserStartAngle = int(userInput)

    userInput = input("Enter laser end angle: ")
    while (is_convertible_to_int(userInput) == False):
        print("Invalid numeric input")
        userInput = input("Enter laser end angle: ")
    laserEndAngle = int(userInput)

    userInput = input("Enter number of steps: ")
    while (is_convertible_to_int(userInput) == False):
        print("Invalid numeric input")
        userInput = input("Enter laser incremental angle: ")
    stepNumber = int(userInput)

    laserIncrement = (laserEndAngle - laserStartAngle) / float(stepNumber)

    print("Start angle=" + str(laserStartAngle))
    print("End angle=" + str(laserEndAngle))
    print("Increment=" + str(laserIncrement))

    # Start threads
    print("running multithreaded laser sweep")

    camera_queue = Queue()
    serial_queue = Queue()

    #user_input_thread = Thread(target=run_user_input, args=(serial_queue, camera_queue,))
    serial_thread = Thread(target=run_serial, args=(serial_queue,))
    camera_thread = Thread(target=run_camera, args=(camera_queue,))

    user_input_thread.start()
    serial_thread.start()
    camera_thread.start()