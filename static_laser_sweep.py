# Importing Libraries 
import serial 
import msvcrt
import cv2
import time
import np

cam_port = 0
cam = cv2.VideoCapture(cam_port)


def is_convertible_to_int(input):
    s = input.strip()
    try:
        int(s)
        return True
    except ValueError:
        return False


arduino = serial.Serial(port='COM3', baudrate=9600, timeout=.1) 


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

laserIncrement = (laserEndAngle - laserStartAngle) / stepNumber;
waitSeconds = 5
capture_count = 0

laserOnCommand = "a:1"
laserOffCommand = "a:1"

servoCommand = "b:" + str(laserStartAngle)
arduino.write(bytes(servoCommand, 'utf-8'))
arduino.write(bytes(laserOnCommand, 'utf-8'))

startTime = time.time()

while capture_count < stepNumber: 
       
    result, image = cam.read()
    if result:
        cv2.imshow("webcam", image)

    data = arduino.readline().decode()
    if(data != ''):
        print(data) # printing the value 

    currentTime = time.time()
    if(currentTime - startTime > waitSeconds):
        fileName = "webcam_" + str(capture_count) + ".png"
        print("saving image")
        cv2.imwrite(fileName, image)
        capture_count += 1
        newServoAngle = np.round(laserStartAngle + capture_count * laserIncrement)
        servoCommand = "b:" + str(laserStartAngle)
        arduino.write(bytes(servoCommand, 'utf-8'))

    if cv2.waitKey(1) == ord('q'):
        break

cam.release()
cv2.destroyAllWindows()

arduino.write(bytes(laserOffCommand, 'utf-8'))