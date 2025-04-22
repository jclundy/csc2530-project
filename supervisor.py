import serial 
import msvcrt
import cv2
import numpy as np

from time import sleep
from threading import Thread
from queue import Queue


def is_convertible_to_float(input):
    s = input.strip()
    try:
        float(s)
        return True
    except ValueError:
        return False

def run_serial(queue):
    print("starting serial thread")
    timeout_setting = 0.01
    arduino = serial.Serial(port='COM3', baudrate=9600, timeout=timeout_setting)
    while True:
        data = arduino.readline().decode()
        if(data != ''):
            print(data) # printing the value
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

def run_user_input(serial_queue, camera_queue):
    print("starting user input thread")
    while True:
        if msvcrt.kbhit():
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
        
        sleep(0.1)

def run_camera(queue):
    print("starting camera thread")

    cam_port = 1
    cam = cv2.VideoCapture(cam_port)
    cam.set(cv2.CAP_PROP_AUTO_EXPOSURE, 3)
    # cam.set(cv2.CAP_PROP_EXPOSURE, -6)  # Set exposure time to -6 (in log base 2)
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)  # Set the resolution to 1280x720
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    capture_count = 0

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
                break
            elif(command_tuple[0] == 'e'):
                exposure = command_tuple[1]
                cam.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
                cam.set(cv2.CAP_PROP_EXPOSURE, exposure)
            elif(command_tuple[0] == 's'):
                baseName = command_tuple[1]
                fileName = baseName + str(capture_count) + ".png"
                cv2.imwrite(fileName, image)
                capture_count += 1
            elif(command_tuple[0] == 'ae'):
                cam.set(cv2.CAP_PROP_AUTO_EXPOSURE, 3)

        cv2.waitKey(1)

if __name__ == '__main__':
    print("running multithreaded supervisor")

    camera_queue = Queue()
    serial_queue = Queue()

    user_input_thread = Thread(target=run_user_input, args=(serial_queue, camera_queue,))
    serial_thread = Thread(target=run_serial, args=(serial_queue,))
    camera_thread = Thread(target=run_camera, args=(camera_queue,))

    user_input_thread.start()
    serial_thread.start()
    camera_thread.start()