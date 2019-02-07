"""
Created on Wed Oct 17 02:23:45 2018

Python 3

@author: bob
"""

import tensorflow as tf
import models
import load_data
import matplotlib.pyplot as plt

from keras.callbacks import ModelCheckpoint

# Initialize some variables
batch_size = 20
train_split = 0.8
val_split = 0.2
seq_length = 0

# Load training data
train_generator = load_data.train_generator(batch_size, seq_length, train_split, seq_train = False)

# Load validation data
val_generator = load_data.val_generator(batch_size, seq_length, val_split, seq_train = False)

# Initialize steps per epoch, validation steps and number of epochs
steps = 126                                                                    # Number of steps before finishing each epoch. Usually, it should be total training data / batch size
val_steps = 31                                                                # Number of steps for validation before finishing each epoch. Usually, it should be total validation data / batch size
epochs = 100

# Build and summaries model
model = models.PilotNet()
model.summary()

checkpointer = ModelCheckpoint(filepath = 'best_weights/weights.best.test.h5',
                               verbose = 1,
                               save_best_only = True)

# Use GPU to train
with tf.device('/gpu:0'):
    # Train using custom generator
    history = model.fit_generator(generator = train_generator,
                       epochs = epochs,
                       validation_data = val_generator,
                       steps_per_epoch = steps,
                       validation_steps = val_steps,
                       callbacks = [checkpointer],
                       verbose = 1)

    # Plot the loss/accuracy
    loss = history.history['loss']
    val_loss = history.history['val_loss']

    plt.figure(figsize = [8, 6])
    plt.plot(loss, 'bo', label = 'Training loss')
    plt.plot(val_loss, 'b', label = 'Validation loss')
    plt.title('Training and validation loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss/Accuracy')
    plt.legend()

    plt.show()

    # Save model
    model.save('trained_model/test.h5')
