

#include <Encoder.h>
#include <EEPROM.h>

#include <WiFiNINA.h>
#include <WiFiUdp.h>
#include <ArduinoMDNS.h>
#include <OSCMessage.h>
#include <OSCBundle.h>
#include <OSCBoards.h>

#include "Wire.h"

#include "arduino_secrets.h"
char ssid[] = SECRET_SSID;        // your network SSID (name)
char pass[] = SECRET_PASS; // your network password (use for WPA, or use as key for WEP)
int status = WL_IDLE_STATUS;     // the Wifi radio's status

IPAddress server_ip;
bool server_ready = false;
int server_ip_len = 0;

OSCErrorCode error;

// A UDP instance to let us send and receive packets over UDP
WiFiUDP udp_mdsn;
WiFiUDP udp_osc;
MDNS mdns(udp_mdsn);
const unsigned int tcp_port = 5555;
WiFiServer server(tcp_port);
WiFiClient client;

IPAddress broadcast_ip(0, 0, 0, 0);
const unsigned int server_port = 3333;
int size = 0;

const int relay1 = 9;
const int motor_forward = 8;
const int motor_reverse = 11;

const int Pressure = A5;// Pressure Sensing
int PWM = 0;
int Inverse_PWM = 0;
int level = 0;

Encoder myEnc(2, 7); //  Set up the linear actuator encoder using pins which support interrupts, avoid using pins with LEDs attached i.e. 13
long oldPosition  = -99999; //   intializing it with random negative value
long oldPressure  = -99999; //   intializing it with random negative value
int currentPosition  = -99999; //   intializing it with random negative value
int correction = 0;
long newPressure=0;


void printMacAddress(byte mac[]) {
  for (int i = 5; i >= 0; i--) {
    if (mac[i] < 16) {
      Serial.print("0");
    }
    Serial.print(mac[i], HEX);
    if (i > 0) {
      Serial.print(":");
    }
  }
  Serial.println();
}

void printWifiData() {
  // print your board's IP address:
  IPAddress ip = WiFi.localIP();
  Serial.print("Local IP Address: ");
  Serial.println(ip);

  // print your MAC address:
  byte mac[6];
  WiFi.macAddress(mac);
  Serial.print("MAC address: ");
  printMacAddress(mac);

  IPAddress gateway_ip = WiFi.gatewayIP();
  Serial.print("GateWay IP Address: ");
  Serial.println(gateway_ip);

}

void printCurrentNet() {
  // print the SSID of the network you're attached to:
  Serial.print("SSID: ");
  Serial.println(WiFi.SSID());

  // print the MAC address of the router you're attached to:
  byte bssid[6];
  WiFi.BSSID(bssid);
  Serial.print("BSSID: ");
  printMacAddress(bssid);

  // print the received signal strength:
  long rssi = WiFi.RSSI();
  Serial.print("signal strength (RSSI):");
  Serial.println(rssi);

  // print the encryption type:
  byte encryption = WiFi.encryptionType();
  Serial.print("Encryption Type:");
  Serial.println(encryption, HEX);
  Serial.println();
}


void setup() {
  pinMode(Pressure, INPUT); //Pressure Sensor
  pinMode(relay1, OUTPUT); //Initiates Motor Channel A pin
  pinMode(motor_forward, OUTPUT); //Initiates Brake Channel A pin
  pinMode(motor_reverse, OUTPUT); //Initiates Brake Channel A pin
  Serial.begin(9600);
  correction = EEPROMReadInt(1); // reading the last position of motor from EEPROM to later caliberate HallEffect sensor values
  


  digitalWrite(LED_BUILTIN, HIGH);
  if (WiFi.status() == WL_NO_SHIELD) {
    Serial.println("Communication with WiFi module failed!");
    // don't continue
    while (true);
  }

  String fv = WiFi.firmwareVersion();
  if (fv < "1.0.0") {
    Serial.println("Please upgrade the firmware");
  }

  // attempt to connect to Wifi network:
  while (status != WL_CONNECTED) {
    Serial.print("Attempting to connect to WPA SSID: ");
    Serial.println(ssid);
    // Connect to WPA/WPA2 network:
    status = WiFi.begin(ssid, pass);

    // wait 10 seconds for connection:
    delay(10000);
  }

  // you're connected now, so print out the data:
  Serial.print("You're connected to the network");
  printCurrentNet();
  printWifiData();

  Serial.println("\nStart listening to get our servers IP");
  server.begin();

  Serial.println("\nStarting connection to server...");
  udp_osc.begin(server_port);

  Serial.println("\nStarting Service Discovery...");

  mdns.begin(WiFi.localIP(), "Pixel1");

  char a1[] = "sensor1=/Pressure1:0%600";
  char a2[] = "actuator1=/Motor1:0%1000";

  char txt[100] = { '\0' };

  txt[0] = (uint8_t) strlen(a1);
  int txt_len = 1;
  for (uint8_t i = 0; i < strlen(a1); i++) {
    if (a1[i] != '\0')
    {
      txt[txt_len] = a1[i];
      txt_len++;
    }
  }

  txt[txt_len] = (uint8_t) strlen(a2);
  txt_len++;
  for (uint8_t i = 0; i < strlen(a2); i++) {
    if (a2[i] != '\0') {
      txt[txt_len] = a2[i];
      txt_len++;
    }
  }

  int success;
  success = mdns.addServiceRecord("Pixel 1._osc", 3333,
      MDNSServiceUDP, txt);

  if (success) {
    Serial.println("Successfully registered service");
  } else {
    Serial.println("Something went wrong while registering service");
  }

  digitalWrite(LED_BUILTIN, LOW);
}


void motor(OSCMessage &msg) {
  newPressure = msg.getFloat(0);

}

void loop() {

 client = server.available();   // listen for incoming clients

 if (client) {                             // if you get a client,
    String currentLine = ""; // make a String to hold incoming data from the client
    while (client.connected()) {        // loop while the client's connected
      if (client.available()) { // if there's bytes to read from the client
        //Serial.println(client.remoteIP());
        if (client.remoteIP() != broadcast_ip) {
          char c;
          do {
            c = client.read();
            currentLine += c; // add it to the end of the currentLine
            server_ip_len++;
          } while (c != -1 || &c == "\n");
        } else {
          break;
        }
      }
    }
    // close the connection:
    client.flush();
    Serial.println(client.status());
    client.stop();
    Serial.println("Client disonnected");

    char ip_str[server_ip_len];
    currentLine.toCharArray(ip_str, server_ip_len);
    ip_str[server_ip_len] = '\0';
    server_ip.fromString(ip_str);
    Serial.print("Server IP: ");
    Serial.println(server_ip);
    server_ready = true;
  }

  if (server_ready == true) {
    

    //// Sending ////
    OSCMessage send_msg_pressure("/Pressure1");
    send_msg_pressure.add(analogRead(Pressure));
    udp_osc.beginPacket(server_ip, server_port);
    send_msg_pressure.send(udp_osc); // send the bytes to the SLIP stream
    udp_osc.endPacket(); // mark the end of the OSC Packet
    send_msg_pressure.empty(); // free space occupied by message
    //// End ////


  //// Main Code //// 
  if (oldPressure > 19 &&  currentPosition > level )
  {
    retractActuator();
  }
  else
  {
    if (currentPosition < level - 100)
    {
      extendActuator();
    }
    else
    {
      stopActuator();
    }

  }

  
  if (newPressure != oldPressure) {
    oldPressure = newPressure;
    PWM = map(newPressure, 300, 600, 0, 255);   // speed for retraction
    Inverse_PWM = map(newPressure, 600, 300, 0, 255);   // speed for extraction
    level = map(newPressure, 200, 600, 12550, 0);
  }

  long newPosition = myEnc.read();  //check the encoder to see if the position has changed
  if (newPosition != oldPosition) {
    oldPosition = newPosition;
    currentPosition = newPosition +correction; //caliberating the motor position
    
  }

  if (newPressure <5) {
    EEPROMWriteInt(1, currentPosition);
  }
  

  
  Serial.println(currentPosition);
  //// End //// 
  
  //// Recieving ////
    OSCMessage recieve_msg("/Pressure1");
    size = udp_osc.parsePacket();
    //Serial.println(udp_osc.remoteIP());

    if (udp_osc.remoteIP() == server_ip) {
      if (size > 0) {
        while (size--) {
          recieve_msg.fill(udp_osc.read());
        }

        if (!recieve_msg.hasError()) {
          recieve_msg.dispatch("/Motor1", motor);
          
        } else {
          error = recieve_msg.getError();
          Serial.print("error: ");
          Serial.println(error);
        }
        udp_osc.flush();
      }
    }
    //// End ////
  }
  mdns.run();
  delay(10);

}
/*
void setup() {
   pinMode(Pressure, INPUT); //Pressure Sensor
  pinMode(relay1, OUTPUT); //Initiates Motor Channel A pin
  pinMode(motor_forward, OUTPUT); //Initiates Brake Channel A pin
  pinMode(motor_reverse, OUTPUT); //Initiates Brake Channel A pin
  Serial.begin(9600);
  //correction = EEPROMReadInt(1); // reading the last position of motor from EEPROM to later caliberate HallEffect sensor values
  retractActuator();
  delay(100000);
  EEPROMWriteInt(1, 0);
  correction = 0;
  }
  void loop(){

}*/
void extendActuator() {
  digitalWrite(motor_forward, HIGH);
  digitalWrite(motor_reverse, LOW);
  analogWrite(relay1, Inverse_PWM);
  
}

void retractActuator() {
  digitalWrite(motor_forward, LOW);
  digitalWrite(motor_reverse, HIGH);
  analogWrite(relay1, PWM);
  
}

void stopActuator() {
  
  analogWrite(relay1, 0);
  digitalWrite(motor_forward, LOW);
  digitalWrite(motor_reverse, LOW);
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
