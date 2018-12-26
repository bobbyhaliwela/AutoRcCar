"""
Created on Tue Oct 23 22:41:35 2018

Python 3

@author: bob

Install pigpio on raspberrypi: http://abyz.me.uk/rpi/pigpio/download.html
PiCamera rapid capture and streaming: https://picamera.readthedocs.io/en/release-1.13/recipes2.html#rapid-capture-and-streaming
"""

import io
import os
import socket
import struct
import picamera
import time
import pigpio
os.system("sudo pigpiod")

from threading import Thread

class SplitFrames(object):
    def __init__(self, connection):

        self.connection = connection
        self.stream = io.BytesIO()
        self.count = 0

    def write(self, buf):

        if buf.startswith(b'\xff\xd8'):
            # Starts of new frame; send the old one's length then the data
            size = self.stream.tell()
            if size > 0:
                self.connection.write(struct.pack('<L', size))
                self.connection.flush()
                self.stream.seek(0)
                self.connection.write(self.stream.read(size))
                self.count += 1
                self.stream.seek(0)
        self.stream.write(buf)

class ClientHelper():
    def __init__(self):

        # Connect to pigpio
        self.pi = pigpio.pi()

        # Initialize IP address and port
        self.host_ip = '192.168.88.242'                                                          # Laptop IP address
        #self.host_ip = '192.168.88.250'                                                          # PC IP address
        self.host_port = 8000                                                                   # Serial port number

        # Create command socket and bind socket to the host
        self.command_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.command_socket.connect((self.host_ip, self.host_port))

        # Create video socket and bind socket to the host
        self.video_socket = socket.socket()
        # self.video_socket.connect((self.host_ip, self.host_port + 1))
        self.video_socket.connect((self.host_ip, self.host_port + 1))
        self.connection = self.video_socket.makefile('wb')

        # Initialize camera and stream
        self.camera = picamera.PiCamera()
        self.camera.resolution = (320, 240)                                                     # pi camera resolution
        self.camera.framerate = 10                                                              # 10 frames/sec
        time.sleep(2)                                                                           # Give 2 secs for camera to initilize
        self.stream = io.BytesIO()

        # Initialize motor and servo BCM pin
        self.motor_gpio = 4
        self.servo_gpio = 17

        # Set neutral value for throttle ang angle
        self.neutral_throttle = 1500
        self.neutral_angle = 1500

        # Add trim angle so the front wheels are centered properly
        self.trim_angle = -30

        # Boolean variable to check the state of receiving command
        self.receive_command = True

        # Initialize necessary variables
        self.drive_speed = 1500
        self.turnAngle = 1500

        # Set motor and servo to neutral position at the start
        self.pi.set_servo_pulsewidth(self.motor_gpio, self.neutral_throttle)
        self.pi.set_servo_pulsewidth(self.servo_gpio, self.neutral_angle + self.trim_angle)

        Thread(target=self.video_stream).start()

    def command(self):
        """

        """

        try:
            print "Rc control..."
            print "Press 'options' to quit the program"

            while self.receive_command:

                # Read command input received from server
                command = self.command_socket.recv(1024).decode()

                # Slice command input
                angle = command[1:4]
                throttle = command[5:8]

                # Angle and throttle values are received in a string format, so it needs to be treated
                # or converted as a float numbers in order to get the correct scaling.

                # Scale turn angle to 450 degrees of turn.
                turn_angle = float(angle) * int(450) / int(255)

                # Scale throttle to 50 units
                vehicle_speed = float(throttle) * int(50) / int(255)

                # Check throttle input, if throttle input == "0", move forward, else, move backward
                if command[4] == "0":
                    speed = self.drive_speed + vehicle_speed
                    self.pi.set_servo_pulsewidth(self.motor_gpio, speed)
                    print "Current speed = " + str(speed)
                else:
                    speed = self.drive_speed - vehicle_speed
                    self.pi.set_servo_pulsewidth(self.motor_gpio, speed)
                    print "Current speed = " + str(speed)

                # Check steering input, turn left if input == "1"
                if command[0] == '1':
                    turn_angle = turn_angle * -1

                angle_turn = self.turnAngle + turn_angle + self.trim_angle
                self.pi.set_servo_pulsewidth(self.servo_gpio, angle_turn)

        finally:
            self.command_socket.close()

    def video_stream(self):
        """

        """

        Thread(target=self.command).start()

        try:
            output = SplitFrames(self.connection)
            self.camera.start_recording(output, format = 'mjpeg')
            self.camera.wait_recording(800)
            self.camera.stop_recording()

            # Write the terminating 0-length to the connection to let the server know we're done
            self.connection.write(struct.pack('<L', 0))

        finally:
            self.connection.close()
            self.video_socket.close()

if __name__ == '__main__':
    ClientHelper()