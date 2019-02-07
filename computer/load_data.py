"""
Created on Sat Jan  5 01:22:58 2019

@author: bob
"""

import scipy.misc
import numpy as np
import glob

def load_data():
    """

    """

    images_list = []
    labels1_list = []
    labels2_list = []

    folder_name = "training_images/"
    filenames = sorted(glob.glob(folder_name + "*.jpg"))

    # Pre-process data
    for i, filename in enumerate(filenames):

        # Get the resized image array
        img_arr = scipy.misc.imresize(scipy.misc.imread(filename)[-90:], [120, 160]) / 255.0

        # Split filename to get the command input
        command = filename[len(folder_name) + 19:43]

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

    return images_list, labels1_list, labels2_list


def load_seq_data(seq_length = 3):
    """

    """

    images_list = []
    labels1_list = []
    labels2_list = []
    x = []

    n_jump = 1
    n_stacked = seq_length

    assert n_jump <= n_stacked

    folder_name = "training_images/"
    filenames = sorted(glob.glob(folder_name + "*.jpg"))

    # Pre-process data
    for i, filename in enumerate(filenames):

        # Load and resize image
        img_arr = scipy.misc.imresize(scipy.misc.imread(filename)[-90:], [120, 160]) / 255.0

        # Split filename to get the command input
        command = filename[len(folder_name) + 19:43]

        # Decompose steering
        steering = int(command[1:4])
        # Bound steering output to constant 255
        steering = steering * scipy.pi / 255

        # Decompose throttle
        throttle = int(command[5:8])
        # Bound throttle output to constant 255
        throttle = throttle * scipy.pi / 255

        # Determine steering input, turn left/right
        if command[0] == "1":
            steering *= -1

        images_list.append(img_arr.astype(np.float32))

        if len(images_list) > n_stacked:
            images_list = images_list[-n_stacked:]

        if (i + 1) >= n_stacked and (i + 1 - n_stacked) % n_jump == 0:
            x.append(np.stack(images_list))

        labels1_list.append(np.float32(steering))
        labels2_list.append(np.float32(throttle))

    return x, labels1_list, labels2_list


def split_train_data(seq_length, split_percentage = 0.8, seq_train = False):
    """
    
    """

    if seq_train == False:

        images_list, labels1_list, labels2_list = load_data()

        # Split data to training set and validation set with 80:20 percentage
        train_x = np.array(images_list[:int(len(images_list) * split_percentage)])
        train_y1 = np.array(labels1_list[:int(len(images_list) * split_percentage)])
        train_y2 = np.array(labels2_list[:int(len(images_list) * split_percentage)])

        return train_x, train_y1, train_y2

    elif seq_train == True:

        images_list, labels1_list, labels2_list = load_seq_data(seq_length)

        # Split data to training set and validation set with 80:20 percentage
        train_x = np.array(images_list[:int(len(images_list) * split_percentage)])
        train_y1 = np.array(labels1_list[:int(len(images_list) * split_percentage)])
        train_y2 = np.array(labels2_list[:int(len(images_list) * split_percentage)])

        return train_x, train_y1, train_y2


def split_val_data(seq_length, split_percentage = 0.2, seq_train = False):
    """
    
    """

    if seq_train == False:

        images_list, labels1_list, labels2_list = load_data()

        # Split data to training set and validation set with 80:20 percentage
        val_x = np.array(images_list[-int(len(images_list) * split_percentage):])
        val_y1 = np.array(labels1_list[-int(len(images_list) * split_percentage):])
        val_y2 = np.array(labels2_list[-int(len(images_list) * split_percentage):])

        return  val_x, val_y1, val_y2

    elif seq_train == True:

        images_list, labels1_list, labels2_list = load_seq_data(seq_length)

        # Split data to training set and validation set with 80:20 percentage
        val_x = np.array(images_list[-int(len(images_list) * split_percentage):])
        val_y1 = np.array(labels1_list[-int(len(images_list) * split_percentage):])
        val_y2 = np.array(labels2_list[-int(len(images_list) * split_percentage):])

        return val_x, val_y1, val_y2


def train_generator(batch_size, seq_length, split_percentage = 0.8, seq_train = False):
    """
    
    """

    train_x, train_y1, train_y2 = split_train_data(seq_length, split_percentage, seq_train)

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

            yield (x_train), [(y1_train), (y2_train)]


def val_generator(batch_size, seq_length, split_percentage = 0.2, seq_train = False):
    """
    
    """

    val_x, val_y1, val_y2 = split_val_data(seq_length, split_percentage, seq_train)

    while True:
        # We don't shuffle validation data
        for index in range(batch_size):
            x_val = val_x[index * batch_size:(index + 1) * batch_size]
            y1_val = val_y1[index * batch_size:(index + 1) * batch_size]
            y2_val = val_y2[index * batch_size:(index + 1) * batch_size]

            yield (x_val), [(y1_val), (y2_val)]