# Smart Implicit Hub

The "Smart Implicit Hub" is the central heart that orchestrates all implicit interaction-based devices. It provides several services in a single system.

* Sensor and actuator discovery
  * Discover sensors and actuators in your local network using MDNS (also known as Bonjour or Avahi).
* Sensor and actuator allocation
  * In case multiple "Smart Implicit Hubs" are running in a local network, one "Hub" can allocate a specific device for itself. The device will then send its data to this "Hub".
* Orchestration of sensor inputs to corresponding actions of actuators
  * Currently only simple mapping of sensor inputs to actuator outputs is implemented.
* Integration of external sensors and actuators (e.g., smart phones)
  * External sensors and actuators that do not support MDNS can be easily integrated and used.

## Getting Started

### Prerequisite

If you run the "Smart Implicit Hub" for the first time, you need to install the python dependencies first.

This application requires python 3 and was tested with python 3.7. You can check your python version with

```bash
python --version
```

To install the necessary requirements run

```bash
pip install -r requirements.txt
```

Furthermore, you need to be in a local network that has an IP starting with "192.....".

### Let's Go

To start the "Smart Implicit Hub" run

```bash
python SmartImplicitHub.py
```

A window will appear that looks as follows:

![00_start](/home/martina/_Code/Smart-Implicit-Hub_public/SmartImplicitHub/doc/00_start.png)

If you have running implicit interaction-based devices, they should appear if you click on the *Discover* button.

![01_discover](/home/martina/_Code/Smart-Implicit-Hub_public/SmartImplicitHub/doc/01_discover.png)

The table shows their IP address, the OSC port, they will listening on, how many sensors and actuators a single device offers, if it is a sensor or an actuator, the OSC path, and also the range of their values (from%to).

#### Running an existing application

If you want to run an already existing application like the "Soma Mattress". Just select Application above the "Save" button and press "Save".

This will lead you to the application tab, where you just have to press the desired application (currently there is only the "Soma Mattress").

![02_application](/home/martina/_Code/Smart-Implicit-Hub_public/SmartImplicitHub/doc/02_application.png)

#### Connecting Sensors Inputs and Actuators Manually

If you want to connect sensor inputs manually with actuators, select the desired device by clicking the checkbox next to it. If you run multiple "Hubs" in the local network, the selected devices should disappear on the other "Hubs". After selecting the desired devices klick "Save".

This will lead you to the "Mapping" tab, where you can connect your sensors (y-axis) with your actuators (x-axis). 

![03_mapping](/home/martina/_Code/Smart-Implicit-Hub_public/SmartImplicitHub/doc/03_mapping.png)

If you select a sensor-actuator-pair a new dialog will open, asking you which mapping function you want to use.

![04_module](/home/martina/_Code/Smart-Implicit-Hub_public/SmartImplicitHub/doc/04_module.png)

Select one module and press save. The dialog will disappear. Now press the "Start OSC Service" button and your sensors should send its sensor readings to the "Hub" while the "Hub" forwards the modified values (according to the selected module) to the actuator.



 ## Code Layout

## Trouble Shooting

## Known Issues

* The SomaMattress application does not allocate the sensors and actuators. Other SomoServers could allocate them, thus the sensors will send their data to the new server.