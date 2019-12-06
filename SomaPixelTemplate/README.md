# SomaPixel Template

This README consists of two parts.

* Installing the necessary libraries and performing the necessary code modifications to run a SomaPixel
* Explaining code snippets

Note that only the steps for the Arduino Wifi Rev. 2 are explained. The routine might change with another board.

## Installing the necessary libraries and performing the necessary code modifications

### Encoder

Download the Encoder library (https://github.com/PaulStoffregen/Encoder) to the Arduino's library folder. Please do not use Arduino's Library Manager as this results in compile errors.

#### MDNS 

MDNS is also known as Bonjour (MacOS, Windows) or Avahi (Linux) and it is used for service discovery.


First install "WiFiNINA" which is a Wifi library for Arduino Wifi Rev2 using Library Manager <b>(Tools > Manage Libraries…)</b>. Download the ArduinoMDSN code (https://github.com/arduino-libraries/ArduinoMDNS) to Arduino's library folder.

To be able to compile the code for the Arduino Wifi Rev2, you should go to the folder, where files for the Arduino Wifi Rev2 board are located. 

In Ubuntu, e.g., 
`/home/martina/.arduino15/packages/arduino/hardware/megaavr/1.6.25/cores/arduino/api`

In Windows, e.g.,

```bash
C:\Users\<UserName>\AppData\Local\Arduino15\packages\arduino\hardware\megaavr\1.8.5\cores\arduino\api\
```

In the `Udp.h` file, add the following line

```
virtual uint8_t beginMulticast(IPAddress, uint16_t) { return 0; }  // initialize, start listening on specified multicast IP address and port. Returns 1 if successful, 0 on failure
```

The code, thus, looks like:

```
public:
  virtual uint8_t begin(uint16_t) =0;   // initialize, start listening on specified port. Returns 1 if successful, 0 if there are no sockets available to use
  virtual uint8_t beginMulticast(IPAddress, uint16_t) { return 0; }  // initialize, start listening on specified multicast IP address and port. Returns 1 if successful, 0 on failure
  virtual void stop() =0;  // Finish with the UDP socket
  ...
```

The project should compile now without errors.
Do not forget to create the `arduino_sectrets.h`  with your credentials. It looks as follows:

```
#define SECRET_SSID "MySSID"
#define SECRET_PASS "MyPassword"
```

However, if you use the TXT record (WHICH WE DO!!) to transmit additional information like OSC paths, the packets become <b>malicious</b>. To fix this, go to `MDNS.cpp` in the ArduinoMDSN code in the function `MDNSError_t MDNS::_sendMDNSMessage(...)` and look for the line `int slen = strlen((char*)this->_serviceRecords[serviceRecord]->textContent)`. This line and the following have to look like:
```
int slen = strlen((char*) this->_serviceRecords[serviceRecord]->textContent);
if (slen > 0) {
	slen -= 1;
}
*((uint16_t*) buf) = ethutil_htons(slen);
```

Now you are done :)

#### OSC

Install the OSC library from the Library Manager :-)

## Code Snippets

### MDNS

In `void setup() ` you start with

```c++
mdns.begin(WiFi.localIP(), "SomaPixel");
```

whereas "SomaPixel" is just a name that we give for this service.

The "Smart Implicit Hub" expects one or several OSC paths from each device.  These are created, e.g., with

```c++
char a1[] = "sensor1=/Pressure1:0%600";
char a2[] = "actuator1=/Motor1:0%1000";

char txt[100] = { '\0' };

txt[0] = (uint8_t) strlen(a1);
int txt_len = 1;
for (uint8_t i = 0; i < strlen(a1); i++) {
 	if (a1[i] != '\0') {
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
```

To start MDNS run

```c++
int success;
success = mdns.addServiceRecord("Pixel 1._osc", 3333, MDNSServiceUDP, txt);

if (success) {
	Serial.println("Successfully registered service");
} else {
    Serial.println("Something went wrong while registering service");
}
```

The devices are now broadcasting their "service" (sensor type, OSC path and sensor range) in the network. A "Smart Implicit Hub" can now allocate this device by sending its IP address.

The routine for receiving the IP address is int the ```void loop()``` function and looks as follows:

```C++
client = server.available();   // listen for incoming clients

if (client) {                             // if you get a client,
	String currentLine = ""; // make a String to hold incoming data from the client
    while (client.connected()) {        // loop while the client's connected
    	if (client.available()) { // if there's bytes to read from the client
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
```

Your code, especially OSC related code should come after

```c++
if (server_ready == true) {
	// Your code if condition is fulfilled
}
```

