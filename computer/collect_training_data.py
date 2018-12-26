"""
Created on Tue Oct 1 22:41:35 2018

Python 3

@author: bob

Most of the code below are taken from Uvindu J Wijesinghe (2017) RCAutoPilot project: https://github.com/UvinduW/RCAutopilot
"""

import cv2
import pygame
import socket
import io
import struct
import time
import numpy as np

from PIL import Image
from threading import Thread

class CollectTrainingData(object):
    def __init__(self):

        # Create socket
        self.picam_socket = socket.socket()
        self.command_socket = socket.socket()

        # Allow immediate reuse of address and prevent error causes by too small delay between executions
        self.picam_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.command_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Bind socket to client - PC
        #self.picam_socket.bind(("192.168.1.101", 8001))
        #self.command_socket.bind(("192.168.1.101", 8000))

        # Bind socket to client - laptop
        self.picam_socket.bind(("192.168.88.242", 8001))
        self.command_socket.bind(("192.168.88.242", 8000))

        # Listen to client
        self.picam_socket.listen(0)
        self.command_socket.listen(0)

        # Accept single connection
        self.picam_client = self.picam_socket.accept()[0].makefile('rb')
        self.command_client, self.addr = self.command_socket.accept()

        # Variable for storing command input in string format
        self.command_input = "00000000"

        # Boolean variable to check command sending state
        self.send_command = True

        # Variable to store value to wait between command transmitted
        self.transmission_interval = 0.00

        # Variable to check the state of start/stop saving streamed image
        self.start_saving = 0

        # Initialize pygame, and pygame joystick object
        pygame.init()
        pygame.joystick.init()
        self.gamepad = pygame.joystick.Joystick(0)
        self.gamepad.init()

        # Start Thread 1
        Thread(target=self.collect_data).start()

    # Thread 2 - Get input command from the user
    def get_input(self):
        """

        """

        # Throttle and reverse fix variables
        throttle_pressed = 0
        reverse_pressed = 0

        # Start the loop to get input command from the user
        while self.send_command:

            pygame.event.pump()

            # Initialize gamepad event
            steering = self.gamepad.get_axis(0)
            throttle = self.gamepad.get_axis(5)
            reverse_throttle = self.gamepad.get_axis(2)

            # Gamepad doesn't initialize throttle to 0 until they are pressed for the first time.
            # This behaviour is fixed to ensure correct inputs are obtained.

            # Throttle fix
            if throttle_pressed == 0:
                if throttle == 0 or throttle == -1:
                    throttle = -1.0
                else:
                    throttle_pressed = 1

            # Reverse fix
            if reverse_pressed == 0:
                if reverse_throttle == 0 or reverse_throttle == -1:
                    reverse_throttle = -1.0
                else:
                    reverse_pressed = 1

            # Scale axes to 255
            throttle = int((throttle + 1) * 127.5)
            reverse_throttle = int((reverse_throttle + 1) * 127.5)
            steering = int(steering * 255)

            # In this project, command input is send to the raspberry pi in a string format.
            # A binary string format (0 or 1) is used to store command input of moving forward/backward,
            # and turn right/left. While a three digit string format is used to store the axis value
            # of both the steering input and the throttle input.
            # These strings are also used for labeling the data.

            # Determine throttle direction, move forward/backward
            if reverse_throttle > 0:
                throttle = reverse_throttle
                throttle_direction = "1"
            else:
                throttle_direction = "0"

            # Determine steering direction, turn left/right
            if steering < 0:
                # Left turn
                steering_direction = "1"
                steering *= -1
            else:
                # Right turn
                steering_direction = "0"

            # Turn angle
            if steering == 0:
                steering_angle = "000"
            elif steering < 10:
                steering_angle = "00" + str(steering)
            elif steering < 100:
                steering_angle = "0" + str(steering)
            else:
                steering_angle = str(steering)

            # Throttle
            if throttle == 0:
                throttle_input = "000"
            elif throttle < 10:
                throttle_input = "00" + str(throttle)
            elif throttle < 100:
                throttle_input = "0" + str(throttle)
            else:
                throttle_input = str(throttle)

            # Construct command input
            self.command_input = steering_direction + steering_angle + throttle_direction + throttle_input

        # Stop the car if thread is terminated
        self.command_input = "00000000"

    def stream_image(self):
        """

        """

        len_stream_image = 0
        stream_image = 0

        # Repeat until a valid image has been received from the client (ie no errors)
        while len_stream_image != 230400:
            # Read the length of the image as a 32-bit unsigned int. If the
            # length is zero, quit the loop
            image_len = struct.unpack('<L', self.picam_client.read(struct.calcsize('<L')))[0]
            if not image_len:
                print("Break as image length is null")
                return 0
            # Construct a stream to hold the image data and read the image
            # data from the connection
            image_stream = io.BytesIO()
            image_stream.write(self.picam_client.read(image_len))
            # Rewind the stream, open it as an image with PIL
            image_stream.seek(0)
            stream_image = Image.open(image_stream)
            # Convert image to numpy array
            stream_image = np.array(stream_image)

            # Check to see if full image has been loaded - this prevents errors due to images lost over network
            len_stream_image = stream_image.size
            if len_stream_image != 230400:
                # The full 320x240 image has not been received
                print("Image acquisition error. Retrying...")

        # Convert to RGB from BRG
        stream_image = stream_image[:, :, ::-1]

        return stream_image

    def collect_data(self):
        """

        """

        try:
            print("Collect training data...")
            print("Press 'R2' or 'L2' to move forward/backward")
            print("Move 'L3' to turn left/turn right")
            print("Press 'round' button to start saving streamed image")
            print("Press 'square' button to stop saving streamed image")
            print("Press 'options' to quit the program")

            # Variables to store the last time command was sent and total number of frames
            last_send_time = 0
            total_frame = 0

            # Variable to store number of images being saved
            image_num = 0

            # Start getting command input (Thread 2)
            Thread(target=self.get_input).start()

            while self.send_command:

                # Load streamed image
                image = self.stream_image()

                if len(image) == 0:
                    break

                # Count total number of frames
                total_frame += 1

                # Logic to handle start save/stop saving streamed image
                if self.gamepad.get_button(1) == 1:
                    self.start_saving = 1 + self.start_saving
                    print("Start saving streamed image")

                    # Delay to prevent double press being detected
                    time.sleep(0.5)

                elif self.gamepad.get_button(3) == 1:
                    self.start_saving = 0
                    print("Stop saving streamed image")

                    # Delay to prevent double press being detected
                    time.sleep(0.5)

                # Write streamed images to disk when start saving streamed image
                if self.start_saving == 1:
                    cv2.imwrite('training_images/frame{:>05}_command-{}.jpg'.format(image_num, self.command_input), image)
                    image_num += 1

                # TODO check if this part of the code is not needed
                # Send commands to car no quicker than the specified transmission interval
                time_interval = time.time() - last_send_time
                if time_interval < self.transmission_interval:
                    wait_time = self.transmission_interval - time_interval
                    print("Wait time = " + str(wait_time))
                    time.sleep(wait_time)

                # Send command and calculate last send time
                self.command_client.send(self.command_input.encode())
                last_send_time = time.time()

                # Quit program
                if self.gamepad.get_button(9) == 1:
                    self.send_command = False
                    break

        finally:
            # Close connection to client in orderly fashion
            self.picam_socket.close()
            self.command_socket.close()
            self.picam_client.close()
            self.command_client.close()

if __name__ == '__main__':
    CollectTrainingData()