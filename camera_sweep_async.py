from common import *
from threading import Thread
from queue import Queue
import time
import os
import numpy as np

def run_command_sequence(queue, params, serial_queue, camera_queue):
    panStartAngle = params["panStartAngle"]
    panIncrement = params["panIncrement"]
    numSteps = params["numSteps"]
    baseDir = params["baseDir"]
    laserAngle = params["laserAngle"]
    tiltAngle = params["tiltAngle"]

    print("beginning run thread")
    print("panStartAngle=" +str(panStartAngle))
    print("panIncrement=" + str(panIncrement))
    print("numSteps=" + str(numSteps))
    print("baseDir=" + str(baseDir))
    print("laserAngle=" + str(laserAngle))
    print("tiltAngle=" + str(tiltAngle))

    print("setting pan angle")
    panAngleCommand = "c:" + str(panStartAngle)  + "\n"
    currentPanAngle = panStartAngle
    serial_queue.put(('s', panAngleCommand))
    time.sleep(2)

    print("setting tilt angle")
    tiltAngleCommand = "d:" + str(tiltAngle)  + "\n"
    currentTiltAngle = tiltAngle
    serial_queue.put(('s', tiltAngleCommand))
    time.sleep(2)

    print("setting laser angle")
    laserAngleCommand = "b:" + str(laserAngle) + "\n"
    currentLaserAngle = laserAngle
    serial_queue.put(('s', laserAngleCommand))
    time.sleep(2)

    laserOnCommand = "a:1\n"
    laserOffCommand = "a:0\n"

    serial_queue.put(('s', laserOffCommand))
    time.sleep(1)

    imagesPath = os.path.join(baseDir, "images")
    laserImgPath = os.path.join(imagesPath, "laserOn")
    regularImgPath = os.path.join(imagesPath, "laserOff")

    if not os.path.exists(imagesPath):
        os.makedirs(imagesPath)
    if not os.path.exists(laserImgPath):
        os.makedirs(laserImgPath)
    if not os.path.exists(regularImgPath):
        os.makedirs(regularImgPath)

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

            # 1 Save regular image - laser off
            imageFileName = os.path.join(regularImgPath, "capture_") + str(i) + ".png"
            print("saving image file at " + imageFileName)
            save_command = ('sn', imageFileName)
            camera_queue.put(save_command)
            time.sleep(0.1)
            # 2 Turn laser on 
            serial_queue.put(('s', laserOnCommand))
            # wait 1 second
            time.sleep(1)
            # 3 Save image with laser on
            laserImageFileName = os.path.join(laserImgPath, "laser_") + str(i) + ".png"
            print("saving image file at " + laserImageFileName)
            save_command = ('sn', laserImageFileName)
            camera_queue.put(save_command)
            # wait 0.1 seconds
            time.sleep(0.1)
            # 4 turn laser off
            serial_queue.put(('s', laserOffCommand))
            # 5 move pan servo to next position
            print("setting pan angle")
            currentPanAngle = np.round(panStartAngle + (i+1) * panIncrement)
            panAngleCommand = "c:" + str(currentPanAngle)  + "\n"
            serial_queue.put(('s', panAngleCommand))
            # wait 5 seconds
            time.sleep(5)



    print("creating log file")
    logPath = baseDir + "/"
    logPath = os.path.join(baseDir, "pose.csv")
    logFile = open(logPath, "a")

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

    userInput = input("Enter laser angle: ")
    while (is_convertible_to_int(userInput) == False):
        print("Invalid numeric input")
        userInput = input("Enter laser angle: ")
    laserAngle = int(userInput)

    userInput = input("Enter tilt angle: ")
    while (is_convertible_to_int(userInput) == False):
        print("Invalid numeric input")
        userInput = input("Enter tilt angle: ")
    tiltAngle = int(userInput)

    userInput = input("Enter pan start angle: ")
    while (is_convertible_to_int(userInput) == False):
        print("Invalid numeric input")
        userInput = input("Enter pan start angle: ")
    panStartAngle = int(userInput)


    userInput = input("Enter pan end angle: ")
    while (is_convertible_to_int(userInput) == False):
        print("Invalid numeric input")
        userInput = input("Enter pan end angle: ")
    panEndAngle = int(userInput)

    userInput = input("Enter pan incremental angle: ")
    while (is_convertible_to_int(userInput) == False):
        print("Invalid numeric input")
        userInput = input("Enter laser incremental angle: ")
    panIncrement = int(userInput)
 
    stepNumber = int(np.round((panEndAngle - panStartAngle + 1) / float(panIncrement)))

    print("Start angle=" + str(panStartAngle))
    print("End angle=" + str(panEndAngle))
    print("Increment=" + str(panIncrement))
    print("Num steps=" + str(stepNumber))

    params = {}
    params["panStartAngle"] =  panStartAngle
    params["panIncrement"] =  panIncrement
    params["numSteps"] =  stepNumber
    params["baseDir"] =  baseDir
    params["laserAngle"] =  laserAngle
    params["tiltAngle"] =  tiltAngle

    # Start threads
    print("running camera sweep routine")

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