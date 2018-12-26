"""
Created on Sat Sep 15 02:52:35 2018

Python 2

This program is use to calibrate the ESC by manually sending maximum and minimum throttle servo pulses values.
In this project, brushed motor is controlled by ESC and they are controlled just like servos.
The pigpio servo pulses starts from 500ms to 2500ms. Normally, we set 1000ms to 2000ms servo pulses
as its minimum and maximum throttle values with 1500ms as its neutral throttle values.

@author: bob

Install pigpio on raspberrypi: http://abyz.me.uk/rpi/pigpio/download.html
"""

import os
import pigpio
os.system ("sudo pigpiod")
import time
time.sleep(1)

class CalibrateEsc(object):
    def __init__(self):

        # Connect to pigpio
        self.pi = pigpio.pi()

        # Initialize motor BCM number
        self.motor_gpio = 4

        # Value for the neutral throttle
        self.neutral_throttle = 1500

        # Set throttle to neutral position before calibrating
        self.pi.set_servo_pulsewidth(self.motor, self.neutral_throttle)
        
        self.calibrate_esc()
        
    def calibrate_esc(self):
        """
        Implementation of ESC calibration. Follow the instructions given by Tamiya
        and write the value for maximum and minimum throttle when asked.
        """

        try:
            print "Starting ESC calibration..."
            print "Follow the instructions given by Tamiya, see the high point setup in the manual"
            print "If you use other brand of ESC, please refer to the instruction manual to calibrate the ESC"
            print "When the instruction ask to provide full throttle, type '2000'"
            print "When the instruction ask to provide full brakes, type '1000'"
            print "When done, press 'q' to quit the program"

            # Start the loop, and wait for the user to type the throttle value
            while True:
                inp = raw_input()
                if inp == "q":
                    print "Quit"
                    break
                else:
                    self.pi.set_servo_pulsewidth(self.motor_gpio, inp)

        finally:
            self.pi.set_servo_pulsewidth(self.motor_gpio, self.neutral_throttle)
            self.pi.stop()

if __name__ == '__main__':
    CalibrateEsc()