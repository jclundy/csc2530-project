from common import *
from threading import Thread
from threading import Event
from queue import Queue
import time
import os
import numpy as np

def run_command_sequence(queue, params, serial_queue, camera_queue, serialEvent, cameraEvent):
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

    event = Event()

    print("waiting 5 seconds for serial line")
    event.wait(5)

    print("setting pan angle: " + str(panStartAngle))
    panAngleCommand = "c:" + str(panStartAngle)  + "\n"
    currentPanAngle = panStartAngle
    serial_queue.put(('s', panAngleCommand))
    serialEvent.wait()

    print("setting tilt angle: " + str(tiltAngle))
    tiltAngleCommand = "d:" + str(tiltAngle)  + "\n"
    currentTiltAngle = tiltAngle
    serial_queue.put(('s', tiltAngleCommand))
    serialEvent.wait()

    print("setting laser angle to: " + str(laserAngle))
    laserAngleCommand = "b:" + str(laserAngle) + "\n"
    currentLaserAngle = laserAngle
    serial_queue.put(('s', laserAngleCommand))
    serialEvent.wait()

    exposureSetting = params["exposureSetting"]
    print("setting exposure to: " + str(exposureSetting))
    camera_queue.put(('e', exposureSetting))
    cameraEvent.wait()

    laserOnCommand = "a:1\n"
    laserOffCommand = "a:0\n"

    print("turning laser off")
    serial_queue.put(('s', laserOffCommand))
    serialEvent.wait()

    print("creating log file")
    logPath = baseDir + "/"
    logPath = os.path.join(baseDir, "pose.csv")
    logFile = open(logPath, "a")

    imagesPath = os.path.join(baseDir, "images")
    laserImgPath = os.path.join(imagesPath, "laserOn")
    regularImgPath = os.path.join(imagesPath, "laserOff")
    laserLowExposurePath = os.path.join(imagesPath, "laserLowExp")

    if not os.path.exists(imagesPath):
        os.makedirs(imagesPath)
    if not os.path.exists(laserImgPath):
        os.makedirs(laserImgPath)
    if not os.path.exists(regularImgPath):
        os.makedirs(regularImgPath)
    if not os.path.exists(laserLowExposurePath):
        os.makedirs(laserLowExposurePath)

    for i in range(0,numSteps+1):
        command_tuple = (None,None)
        if not queue.empty():
            try:
                command_tuple = queue.get(block=False)
            except queue.Empty:
                pass
            if(command_tuple[0]) == 'q':
                return
        else:
            # 0 move pan servo to next position
            currentPanAngle = np.round(panStartAngle + i * panIncrement)
            print("setting pan angle to " + str(currentPanAngle))
            panAngleCommand = "c:" + str(currentPanAngle)  + "\n"
            serial_queue.put(('s', panAngleCommand))
            serialEvent.wait()
            # wait 5 seconds
            event.wait(5)
            
            print("logging current position")
            log_pose(logFile, i, currentLaserAngle, currentPanAngle, currentTiltAngle)

            # 1 Save regular image - laser off
            imageFileName = os.path.join(regularImgPath, "capture_") + str(i) + ".png"
            print("saving image file at " + imageFileName)
            save_command = ('sn', imageFileName)
            camera_queue.put(save_command)
            cameraEvent.wait()

            # wait 1 second
            event.wait(1)
            # 2 Turn laser on
            print("turning laser on") 
            serial_queue.put(('s', laserOnCommand))
            serialEvent.wait()
            # wait 1 second
            event.wait(3)
            # 3 Save image with laser on
            laserImageFileName = os.path.join(laserImgPath, "laser_") + str(i) + ".png"
            print("saving image file at " + laserImageFileName)
            save_command = ('sn', laserImageFileName)
            camera_queue.put(save_command)
            cameraEvent.wait()
            # wait 1 seconds
            event.wait(1)
            # 3b set low exposure
            camera_queue.put(('e', laserExposureSetting))
            cameraEvent.wait()
            event.wait(1)
            # save image
            laserImageFileName = os.path.join(laserLowExposurePath, "laser_low_exp_") + str(i) + ".png"
            print("saving image file at " + laserImageFileName)
            save_command = ('sn', laserImageFileName)
            camera_queue.put(save_command)
            cameraEvent.wait()
            # wait 1 seconds
            event.wait(1)

            # return to regular exposure
            camera_queue.put(('e', exposureSetting))
            cameraEvent.wait()

            # 4 turn laser off
            print("turning laser off")
            serial_queue.put(('s', laserOffCommand))
            serialEvent.wait()
            event.wait(1)
    print("Done !")

def run_user_input(serial_queue, camera_queue, command_queue):
    print("starting user input thread")
    event = Event()
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
        event.wait(0.1)

if __name__ == '__main__':
    # Start threads in background
    camera_queue = Queue()
    serial_queue = Queue()

    camera_event = Event()
    serial_event = Event()

    serial_thread = Thread(target=run_serial, args=(serial_queue,serial_event, ))
    camera_thread = Thread(target=run_camera, args=(camera_queue,camera_event, 2))

    serial_thread.start()
    camera_thread.start()

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
    panIncrement = np.abs(int(userInput))

    userInput = input("Enter default exposure setting: ")
    while (is_convertible_to_int(userInput) == False):
        print("Invalid numeric input")
        userInput = input("Enter default exposure setting: ")
    exposureSetting = int(userInput)

    userInput = input("Enter laser exposure setting: ")
    while (is_convertible_to_int(userInput) == False):
        print("Invalid numeric input")
        userInput = input("Enter laser exposure setting: ")
    laserExposureSetting = int(userInput)

    if(panEndAngle < panStartAngle):
        panIncrement *= -1 
 
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
    params["exposureSetting"] = exposureSetting
    params["laserExposureSetting"] = laserExposureSetting

    # Start threads
    print("running camera sweep routine")

    run_queue = Queue()
    command_thread = Thread(target=run_command_sequence, args=(run_queue, params, serial_queue, camera_queue,serial_event, camera_event,))
    command_thread.start()
    user_thread = Thread(target=run_user_input, args=(serial_queue, camera_queue, run_queue))
    user_thread.start()

    command_thread.join()
    serial_thread.join()
    camera_thread.join()
    user_thread.join()