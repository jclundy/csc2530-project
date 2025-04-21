# Importing Libraries 
import serial 
import time 
import msvcrt

arduino = serial.Serial(port='COM3', baudrate=9600, timeout=.1) 
def write_read(x): 
    arduino.write(bytes(x, 'utf-8')) 
    time.sleep(0.05) 
    return data 

while True: 
    data = arduino.readline().decode()
    if(data != ''):
        print(data) # printing the value 

    if msvcrt.kbhit():
        # command = msvcrt.getch();
        command = input("Enter a number: ") # Taking input from user 
        print("You input: ", command)
        arduino.write(bytes(command, 'utf-8'))
