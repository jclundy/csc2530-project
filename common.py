import serial 
import msvcrt
import cv2
import numpy as np
from threading import Thread
from threading import Event
from queue import Queue

def is_convertible_to_int(input):
    s = input.strip()
    try:
        int(s)
        return True
    except ValueError:
        return False

def is_convertible_to_float(input):
    s = input.strip()
    try:
        float(s)
        return True
    except ValueError:
        return False

def log_pose(file, step, laser, pan, tilt):
    line = str(step) + ", " + str(laser) + ", " + str(pan) + ", " + str(tilt)
    file.write(line)
    file.write("\n")

def run_serial(queue, serialEvent):
    print("starting serial thread")
    timeout_setting = 0.1
    arduino = serial.Serial(port='COM3', baudrate=115200, timeout=timeout_setting)
    
    while True:
        # data = arduino.readline().decode()
        # if(data != ''):
        #     print(data) # printing the value
        if not queue.empty():
            command_tuple = (None,None)
            try:
                command_tuple = queue.get(block=False)
            except queue.Empty:
                pass
            if(command_tuple[0]) == 'q':
                break
            else:
                command = command_tuple[1]
                if command is not None:
                    arduino.write(bytes(command, 'utf-8'))
                    serialEvent.set()

def run_user_input(serial_queue, camera_queue):
    print("starting user input thread")
    event = Event()
    while True:
        command = input("Enter a command: ") # Taking input from user
        print("You input: ", command)
        if(command == 'q'):
            quit_command = ('q', None)
            serial_queue.put(quit_command)
            camera_queue.put(quit_command)
            print("exiting")
            break
        elif(command == 'e'):
            userInput = input("Enter exposure (log base 2): ")
            while (is_convertible_to_float(userInput) == False):
                print("Invalid numeric input")
                userInput = input("Enter exposure (log base 2): ")
            exposure = float(userInput)
            exposure_command = ('e', exposure)
            camera_queue.put(exposure_command)
        elif (command == 's'):
            # capture
            baseName = "webcam_"
            save_command = ('s', baseName)
            camera_queue.put(save_command)
        elif (command == "sn"):
            userInput = input("input filename")
            save_command = ('s', userInput)
            camera_queue.put(save_command)
        elif (command == "ae"):
            command = ('ae', None)
            camera_queue.put(command)
        else:
            serial_command = ('c', command)
            serial_queue.put(serial_command)
        event.wait(0.1)

def run_camera(queue, cameraEvent, cam_port=1):
    print("starting camera thread")

    cam = cv2.VideoCapture(cam_port)
    cam.set(cv2.CAP_PROP_AUTO_EXPOSURE, 3)
    cam.set(cv2.CAP_PROP_AUTOFOCUS, 1)
    # cam.set(cv2.CAP_PROP_EXPOSURE, -6)  # Set exposure time to -6 (in log base 2)
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)  # Set the resolution to 1280x720
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    capture_count = 0

    fps = cam.get(cv2.CAP_PROP_FPS) 
    print("default fps " + str(fps))

    while True:
        result, image = cam.read()
        if result:
            cv2.imshow("webcam", image)

        command_tuple = (None,None)
        if not queue.empty():
            try:
                command_tuple = queue.get(block=False)
            except queue.Empty:
                pass
            if(command_tuple[0]) == 'q':
                cameraEvent.set()
                break
            elif(command_tuple[0] == 'e'):
                exposure = command_tuple[1]
                cam.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
                cam.set(cv2.CAP_PROP_EXPOSURE, exposure)
                cameraEvent.set()
            elif(command_tuple[0] == 's'):
                baseName = command_tuple[1]
                fileName = baseName + str(capture_count) + ".png"
                cv2.imwrite(fileName, image)
                cameraEvent.set()
                capture_count += 1
            elif(command_tuple[0] == 'sn'):
                fileName = command_tuple[1]
                cv2.imwrite(fileName, image)
                cameraEvent.set()
            elif(command_tuple[0] == 'ae'):
                cam.set(cv2.CAP_PROP_AUTO_EXPOSURE, 3)
                cameraEvent.set()
        cv2.waitKey(1)
