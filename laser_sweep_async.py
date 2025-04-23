from common import *
from threading import Thread
from queue import Queue
import time
import os
import numpy as np

def log_pose(file, step, laser, pan, tilt):
    line = str(step) + ", " + str(laser) + ", " + str(pan) + ", " + str(tilt)
    file.write(line)
    file.write("\n")

def run_command_sequence(queue, params, serial_queue, camera_queue):
    laserStartAngle = params["startAngle"]
    laserIncrement = params["laserIncrement"]
    numSteps = params["numSteps"]
    baseDir = params["baseDir"]
    panAngle = params["panAngle"]
    tiltAngle = params["tiltAngle"]

    laserOnCommand = "a:1\n"
    laserOffCommand = "a:0\n"
   
    print("beginning run thread")
    print("laserStartAngle=" +str(laserStartAngle))
    print("laserIncrement=" + str(laserIncrement)) 
    print("numSteps=" + str(numSteps)) 
    print("baseDir=" + str(baseDir)) 
    print("panAngle=" + str(panAngle)) 
    print("tiltAngle=" + str(tiltAngle)) 

    time.sleep(5)

    print("setting pan angle")
    panAngleCommand = "c:" + str(panAngle)  + "\n"
    currentPanAngle = panAngle
    serial_queue.put(('s', panAngleCommand))
    time.sleep(2)

    print("setting tilt angle")
    tiltAngleCommand = "d:" + str(tiltAngle)  + "\n"
    currentTiltAngle = tiltAngle
    serial_queue.put(('s', tiltAngleCommand))
    time.sleep(2)

    print("setting laser angle")
    laserAngleCommand = "b:" + str(laserStartAngle) + "\n"
    currentLaserAngle = laserStartAngle
    serial_queue.put(('s', laserAngleCommand))
    time.sleep(2)

    serial_queue.put(('s', laserOnCommand))
    time.sleep(1)

    print("creating log file")
    logPath = baseDir + "/"
    logPath = os.path.join(baseDir, "pose.csv")
    logFile = open(logPath, "a")

    for i in range(0,numSteps):
        command_tuple = (None,None)
        if not queue.empty():
            try:
                command_tuple = queue.get(block=False)
            except queue.Empty:
                pass
            if(command_tuple[0]) == 'q':
                return
        else:
            log_pose(logFile, i, currentLaserAngle, currentPanAngle, currentTiltAngle)

            imagesPath = os.path.join(baseDir, "images")

            if not os.path.exists(imagesPath):
                os.makedirs(imagesPath)

            imageFileName = os.path.join(imagesPath, "capture_") + str(i) + ".png"
            print("saving image file at " + imageFileName)
            save_command = ('sn', imageFileName)
            camera_queue.put(save_command)
            time.sleep(0.5)
            currentLaserAngle = np.round(laserStartAngle + (i+1) * laserIncrement)
            laserAngleCommand = "b:" + str(currentLaserAngle) + "\n"
            print("moving to next angle:" + str(currentLaserAngle))
            serial_queue.put(('s', laserAngleCommand))
            time.sleep(6)
    # loop - end

    # end of thread
    serial_queue.put(('s', laserOffCommand))
    time.sleep(1)
    quit_command = ('q', None)
    serial_queue.put(quit_command)
    camera_queue.put(quit_command)

def run_user_input(serial_queue, camera_queue, command_queue):
    print("starting user input thread")
    while True:
        command = input("Enter a command: ") # Taking input from user
        print("You input: ", command)
        if(command == 'q'):
            quit_command = ('q', None)
            serial_queue.put(quit_command)
            camera_queue.put(quit_command)
            command_queue.put(quit_command)
            print("exiting")
            break
        time.sleep(0.1)

if __name__ == '__main__':
 
    # User input
    baseDir = input("Enter image folder name: ")

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

    userInput = input("Enter laser incremental angle: ")
    while (is_convertible_to_int(userInput) == False):
        print("Invalid numeric input")
        userInput = input("Enter laser incremental angle: ")
    laserIncrement = int(userInput)
    stepNumber = int(np.round((laserEndAngle - laserStartAngle + 1) / float(laserIncrement)))

    print("Start angle=" + str(laserStartAngle))
    print("End angle=" + str(laserEndAngle))
    print("Increment=" + str(laserIncrement))
    print("Num steps=" + str(stepNumber))

    params = {}
    params["startAngle"] =  laserStartAngle
    params["laserIncrement"] =  laserIncrement
    params["numSteps"] =  stepNumber
    params["baseDir"] =  baseDir
    params["panAngle"] =  105
    params["tiltAngle"] =  0

    # Start threads
    print("running multithreaded laser sweep")

    camera_queue = Queue()
    serial_queue = Queue()
    run_queue = Queue()

    command_thread = Thread(target=run_command_sequence, args=(run_queue, params, serial_queue, camera_queue,))
    serial_thread = Thread(target=run_serial, args=(serial_queue,))
    camera_thread = Thread(target=run_camera, args=(camera_queue,))
    user_thread = Thread(target=run_user_input, args=(serial_queue, camera_queue, run_queue))

    user_thread.start()
    serial_thread.start()
    camera_thread.start()
    command_thread.start()


    command_thread.join()
    serial_thread.join()
    camera_thread.join()
    user_thread.join()