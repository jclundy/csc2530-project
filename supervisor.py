# Importing Libraries 
import serial 
import msvcrt
import cv2

cam_port = 0
cam = cv2.VideoCapture(cam_port)


arduino = serial.Serial(port='COM3', baudrate=9600, timeout=.1) 

capture_count = 0

while True: 

    result, image = cam.read()
    if result:
        cv2.imshow("webcam", image)

    data = arduino.readline().decode()
    if(data != ''):
        print(data) # printing the value 

    if msvcrt.kbhit():
        command = input("Enter a command: ") # Taking input from user
        print("You input: ", command)
        if(command == 'q'):
            print("exiting")
            break
        elif (command == 'c'):
            # capture
            fileName = "webcam_" + str(capture_count) + ".png"
            print("saving image")
            cv2.imwrite(fileName, image)
            capture_count += 1
        else:
            arduino.write(bytes(command, 'utf-8'))

    cv2.waitKey(1)

cam.release()
cv2.destroyAllWindows()