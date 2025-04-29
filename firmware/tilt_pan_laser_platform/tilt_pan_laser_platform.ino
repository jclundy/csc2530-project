#include <Servo.h>
Servo laserServo;
Servo panServo;
Servo tiltServo;

#define LASER_SERVO_PIN 9
#define LASER_ON_PIN 8

#define PAN_SERVO_PIN 11
#define TILT_SERVO_PIN 10


void  setup()
{

  pinMode (LASER_ON_PIN,  OUTPUT);
  laserServo.attach(LASER_SERVO_PIN);
  laserServo.write(70);

  tiltServo.attach(TILT_SERVO_PIN);
  tiltServo.write(0);

  panServo.attach(PAN_SERVO_PIN);
  panServo.write(105);

  Serial.begin(115200);
  while (!Serial);

}


void  loop() {
  if (Serial.available())
  {
    // int state = Serial.parseInt();
    String command = Serial.readString();
    int delimit_idx = command.indexOf(":");
    char command_type = command[0];
    int value = command.substring(delimit_idx+1).toInt();

    // String reply = "Command:";
    // reply += command;
    // reply += "; type:";
    // reply += command_type;
    // reply += "; value:";
    // reply.concat(value);
    // Serial.println(reply);

    // a - laser on / off
    // b - laser angle
    // c - pan
    // d - tilt
    if(command_type == 'a') {
      digitalWrite (LASER_ON_PIN, value);
    } else if(command_type == 'b') {
      laserServo.write(value);
    } else if (command_type == 'c') {
      panServo.write(value);
    } else if (command_type == 'd') {
      if(value <= 110) {
        tiltServo.write(value);
      } 
      // else {
      //   Serial.println("invalid command for tilt servo");
      // }
    }
  }
}



  