"""
Created on Tue Oct 23 22:41:35 2018

Python 3

@author: bob

Most of the code below are taken from Uvindu J Wijesinghe (2017) RCAutoPilot project: https://github.com/UvinduW/RCAutopilot
"""

import cv2
import numpy as np
import scipy.misc
import socket
import io
import struct
import pygame
import time
import tensorflow as tf

from keras.models import load_model
from PIL import Image
from threading import Thread

class AutonomousMode(object):
    def __init__(self):

        # Create socket
        self.picam_socket = socket.socket()
        self.command_socket = socket.socket()

        # Allow immediate reuse of address and prevent error causes by too small delay between executions
        self.picam_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.command_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Bind socket to client - PC
        #self.picam_socket.bind(("192.168.88.241", 8001))
        #self.command_socket.bind(("192.168.88.241", 8000))

        # Bind socket to client - laptop
        self.picam_socket.bind(("192.168.88.242", 8001))
        self.command_socket.bind(("192.168.88.242", 8000))

        # Listen to client
        self.picam_socket.listen(0)
        self.command_socket.listen(0)

        # Accept single connection
        self.picam_client = self.picam_socket.accept()[0].makefile('rb')
        self.command_client, self.addr = self.command_socket.accept()

        # Boolean variable to check command sending state
        self.send_command = True

        # Variable to store value to wait between command transmitted
        self.transmission_interval = 0.00

        # Variable to check the state of autonomous/manual mode. The autonomous mode is set to off at the start
        self.autonomous_mode = 0

        # Variable to store the value of predicted command input
        self.pred_command_input = "00000000"

        # Variable to store the scale of display feeds window
        self.display_scale = 2

        # Initialize pygame, and pygame joystick object
        pygame.init()
        pygame.joystick.init()
        self.gamepad = pygame.joystick.Joystick(0)
        self.gamepad.init()

        # Start Thread 1 - main loop
        Thread(target=self.main_loop).start()

    def get_predicted_input(self, image, model):
        """

        """

        # Resize image and normalize
        resize_img = scipy.misc.imresize(image[-90:], [120, 160]) / 255.0

        # Convert image from 3D tensors to 4D tensors
        feed_image = np.expand_dims(resize_img, axis=0)

        # Predict image
        preds = model.predict(feed_image)

        # Decompose prediction
        steering = preds[0][0][0] * 255 / scipy.pi
        throttle = preds[1][0][0] * 255 / scipy.pi

        # Convert prediction to integer
        steering = steering.astype(dtype=int)
        throttle = throttle.astype(dtype=int)

        # Determine throttle direction, move forward/backward
        if throttle > 0:
            throttle_direction = "0"
        else:
            throttle_direction = "1"

        # Determine steering direction, turn left/right
        if steering < 0:
            steering_direction = "1"
            steering *= -1
        else:
            steering_direction = "0"

        # Convert predicted input to string
        # Turn angle
        steering_angle = str(steering)
        steering_angle = steering_angle.zfill(3)

        # Throttle
        throttle_input = str(throttle)
        throttle_input = throttle_input.zfill(3)

        # Construct predicted command input
        self.pred_command_input = steering_direction + steering_angle + throttle_direction + throttle_input

        return self.pred_command_input

    # Thread 2
    def display_feeds(self, image):
        """

        """

        # Convert to grayscale
        draw_image = Image.fromarray(image)

        # Scale image by user specified scale factor
        basewidth = 320 * self.display_scale
        wpercent = (basewidth / float(draw_image.size[0]))
        hsize = int((float(draw_image.size[1]) * float(wpercent)))
        draw_image = draw_image.resize((basewidth, hsize), Image.ANTIALIAS)

        # Convert back to array for display
        view = np.array(draw_image)

        roi = scipy.misc.imresize(image[-90:], [120, 160])

        # Display feeds
        cv2.imshow("Car View", view)
        cv2.imshow("ROI", roi)

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

        # Convert from BRG to RGB
        stream_image = stream_image[:, :, ::-1]

        return  stream_image

    def main_loop(self):
        """

        """

        try:
            print("Press 'start' button to activate autonomous mode")
            print("Press 'O' button to deactivate autonomous mode")
            print("Press 'options' to quit the program")

            # Load model
            model = load_model('trained_model/pilotnet_linear.h5', custom_objects = {"tf": tf})

            # Variable to store the time of last sent command
            last_send_time = 0

            while self.send_command:
                # Launch pygame event to detect button press
                pygame.event.pump()

                # Load image
                image = self.stream_image()

                # Check image length
                if len(image) == 0:
                    break

                # Display feeds from picamera
                self.display_feeds(image)

                # Logic to handle activating/deactivating autonomous mode
                if self.gamepad.get_button(10) == 1:
                    self.autonomous_mode = 1 + self.autonomous_mode
                    print("Autonomous mode activated")

                    # Delay to prevent double press
                    time.sleep(0.2)

                elif self.gamepad.get_button(1) == 1:
                    self.autonomous_mode = 1 - self.autonomous_mode
                    print("Autonomous mode deactivated")

                    # Delay to prevent double press
                    time.sleep(0.2)

                # Get predicted command input if autonomous mode is activate, else stop the car
                if self.autonomous_mode == 1:
                    # Get predicetd command input
                    self.pred_command_input = self.get_predicted_input(image, model)
                    print("Predicted command input: ", self.pred_command_input)

                elif self.autonomous_mode == 0:
                    self.pred_command_input = "00000000"
                    print("Predicted command input: ", self.pred_command_input)
                    print("Activate autonomous mode to move the car")

                # Send commands to car no quicker than the specified transmission interval
                #time_interval = time.time() - last_send_time
                #if time_interval < self.transmission_interval:
                    #wait_time = self.transmission_interval - time_interval
                    #time.sleep(wait_time)

                # Send predicted command input to car
                self.command_client.send(self.pred_command_input.encode())

                # Quit program
                if cv2.waitKey(1) & self.gamepad.get_button(9) == 1:
                    # Stop the car before quiting the program
                    self.pred_command_input = "00000000"
                    self.command_client.send(self.pred_command_input.encode())
                    break

        finally:
            # Close connection to client in orderly fashion
            self.picam_socket.close()
            self.command_socket.close()
            self.picam_client.close()
            self.command_client.close()

if __name__ == '__main__':
    AutonomousMode()