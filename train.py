"""
Created on Wed Oct 17 02:23:45 2018

Python 3

@author: bob
"""

import tensorflow as tf
import pilotnet
import conv2D
import load_data
import matplotlib.pyplot as plt

from keras.callbacks import ModelCheckpoint

# Initialize number of epochs and batch size
epochs = 300
steps = 152
batch_size = 20

# Load training data
train_generator = load_data.train_generator(batch_size)

# Load validation data
val_generator = load_data.val_generator(batch_size)

# Build and summaries model
model = pilotnet.PilotNet()
model.summary()

#model = conv2D.Convolutional2D()
#model.summary()

checkpointer = ModelCheckpoint(filepath = 'best_weights/weights.best.pilotnet_2.h5',
                               verbose = 1,
                               save_best_only = True)

# Train model using custom generator
with tf.device('/gpu:0'):
    history = model.fit_generator(generator = train_generator,
                       epochs = epochs,
                       validation_data = val_generator,
                       steps_per_epoch = steps,
                       validation_steps = 38,
                       callbacks = [checkpointer],
                       verbose = 1)

    # Plot the loss/accuracy
    loss = history.history['loss']
    val_loss = history.history['val_loss']

    plt.figure(figsize = [8, 6])
    plt.plot(loss, 'bo', label='Training loss')
    plt.plot(val_loss, 'b', label='Validation loss')
    plt.title('Training and validation loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss/Accuracy')
    plt.legend()

    plt.show()

    # Save model
    model.save('trained_model/pilotnet_2.h5')
