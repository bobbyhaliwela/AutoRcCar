"""
Created on Wed Oct 17 02:23:45 2018

Python 3

@author: bob

"""

import scipy.misc
import numpy as np
import glob

images_list = []
labels1_list = []
labels2_list = []

folder_name = "training_images/"

# Load, read and preprocess the training data
for filename in glob.glob(folder_name + "*.jpg"):
    image_filename = filename[len(folder_name):]
    command = filename[len(folder_name) + 19:43]

    # Get the resized image array
    img_arr = scipy.misc.imresize(scipy.misc.imread(folder_name + image_filename)[-90:], [120, 160]) / 255.0

    # Decompose steering
    steering = int(command[1:4])
    # Bound steering output to constant 255
    steering = steering * scipy.pi / 255

    # Decompose throttle
    throttle = int(command[5:8])
    # Bound throttle output to constant 255
    throttle = throttle * scipy.pi / 255

    if command[0] == "1":
        steering *= -1

    images_list.append(img_arr.astype(np.float32))
    labels1_list.append(np.float32(steering))
    labels2_list.append(np.float32(throttle))

# Split data to training set and validation set with 80:20 percentage
train_x = np.array(images_list[:int(len(images_list) * 0.8)])
train_y1 = np.array(labels1_list[:int(len(images_list) * 0.8)])
train_y2 = np.array(labels2_list[:int(len(images_list) * 0.8)])

val_x = np.array(images_list[-int(len(images_list) * 0.2):])
val_y1 = np.array(labels1_list[-int(len(images_list) * 0.2):])
val_y2 = np.array(labels2_list[-int(len(images_list) * 0.2):])

def train_generator(batch_size):

        order = np.arange(len(train_x))

        while True:

            # Shuffle training data
            np.random.shuffle(order)
            x = train_x[order]
            y1 = train_y1[order]
            y2 = train_y2[order]

            for index in range(batch_size):
                x_train = x[index * batch_size:(index + 1) * batch_size]
                y1_train = y1[index * batch_size:(index + 1) * batch_size]
                y2_train = y2[index * batch_size:(index + 1) * batch_size]

                yield [np.array(x_train)], [np.array(y1_train), np.array(y2_train)]

def val_generator(batch_size):

        while True:
            # We don't shuffle validation data
            for index in range(batch_size):
                x_val = val_x[index * batch_size:(index + 1) * batch_size]
                y1_val = val_y1[index * batch_size:(index + 1) * batch_size]
                y2_val = val_y2[index * batch_size:(index + 1) * batch_size]

                yield [np.array(x_val)], [np.array(y1_val), np.array(y2_val)]