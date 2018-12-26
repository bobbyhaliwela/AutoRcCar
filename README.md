# AutoRcCar

**AutoRcCar** is a personal project of the author, used to deepen the author's knowledge of both deep learning in general and how deep learning could be used for self driving car. The project used a 1/10 scale Tamiya RC car and a Raspberry Pi.

## Acknowledgements

**Uvindu J Wijesinghe's RCAutopilot** project, which helped build the foundation of this project, which is to control the rc car using PS4 controller. This project used lots of his code to implement this. You can see his project here: https://github.com/UvinduW/RCAutopilot

## Prerequisites

If you wish to build a similar project, these are the pre-requisites for both hardware and software.

### Hardware

- Raspberry Pi 3
- Raspberry Pi Camera - fish eye is preffered
- 1/10 RC Car
- ESC - usually comes with the RC Car
- Servo
- PS4 controller

### Software

You don't have to install the exact same version of these packages, but be sure to see the documentation of these packages if you are running a newer version.

- Ubuntu 16.04
- Python 3
- Scipy 1.1.0
- OpenCV 3.1.0
- Numpy 1.15.4
- PIL 5.3.0
- PyGame 1.9.4
- TensorFlow 1.11.0
- Keras 2.2.4
- pigpio - install only on raspberry pi: http://abyz.me.uk/rpi/pigpio/download.html
