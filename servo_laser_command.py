# Importing Libraries 
import serial 
import msvcrt

arduino = serial.Serial(port='COM3', baudrate=9600, timeout=.1) 


while True: 


    data = arduino.readline().decode()
    if(data != ''):
        print(data) # printing the value 

    if msvcrt.kbhit():
        command = input("Enter a command: ") # Taking input from user
        print("You input: ", command)
        if(command == 'q'):
            print("exiting")
            break
        else:
            arduino.write(bytes(command, 'utf-8'))