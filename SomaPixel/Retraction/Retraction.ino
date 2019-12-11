#include <Encoder.h>
#include <EEPROM.h>
//#include <WiFiNINA.h>

int leftmotorForward = 8;    // pin 8 --- left motor (+) green wire
int leftmotorBackward = 11; // pin 11 --- left motor (-) black wire
int leftmotorspeed = 9;     // pin 9 --- left motor speed signal
int currentPosition = -99999; //   intializing it with random negative value
long oldPosition = -99999;   //   intializing it with random negative value
long newPressure = -99999;   //   intializing it with random negative value
long oldPressure = -99999;   //   intializing it with random negative value

int PWM = 0;
int Inverse_PWM = 0;
int level = 0;
int correction = 0;
const int Pressure = A5;// Pressure Sensing

Encoder myEnc(2, 7);  //  Set up the linear actuator encoder using pins which support interrupts, avoid using pins with LEDs attached i.e. 13

//------------------------------------------------------

void setup() //---3 Pins being used are outputs---
{
  pinMode(leftmotorForward, OUTPUT);
  pinMode(leftmotorBackward, OUTPUT);
  pinMode(leftmotorspeed, OUTPUT);
  Serial.begin(9600);
  correction = EEPROMReadInt(1);  // reading the last position of motor from EEPROM to later caliberate HallEffect sensor values

}

// ---Main Program Loop -----------------------------

void loop()
{

  retractActuator();
  EEPROMWriteInt(1, 0);
}


void extendActuator()
{
  analogWrite(9, Inverse_PWM);
  digitalWrite(11, LOW); // Drives LOW outputs down first to avoid damage
  digitalWrite(8, HIGH);

}

void retractActuator()
{
  analogWrite(9, 255);
  digitalWrite(8, LOW); // Drives LOW outputs down first to avoid damage
  digitalWrite(11, HIGH);
}

void Stop() // Sets speed pins to LOW disabling both motors
{
  digitalWrite(9, LOW);
  digitalWrite(11, LOW);
  digitalWrite(8, LOW);
}

void EEPROMWriteInt(int address, int value)
{
  byte two = (value & 0xFF);
  byte one = ((value >> 8) & 0xFF);

  EEPROM.update(address, two);
  EEPROM.update(address + 1, one);
}

int EEPROMReadInt(int address)
{
  long two = EEPROM.read(address);
  long one = EEPROM.read(address + 1);

  return ((two << 0) & 0xFFFFFF) + ((one << 8) & 0xFFFFFFFF);
}
