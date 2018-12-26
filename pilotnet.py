import tensorflow as tf

from keras.models import Model
from keras.layers import Activation, BatchNormalization, Conv2D, Dense, Dropout, Flatten, Input, Lambda
from keras.optimizers import Adam
from keras import regularizers

def PilotNet():
    """
    Construct PilotNet architecture as described in https://arxiv.org/pdf/1704.07911.pdf

    """

    img_height = 120
    img_width = 160
    img_channels = 3

    input_shape = Input(shape = (img_height, img_width, img_channels), name = 'input_shape')

    X = input_shape

    # PilotNet five convolutional layers
    X = Conv2D(filters = 24, kernel_size = (5, 5), strides = (2, 2), activation = 'relu')(X)
    X = Conv2D(filters = 36, kernel_size = (5, 5), strides = (2, 2), activation = 'relu')(X)
    X = Conv2D(filters = 48, kernel_size = (5, 5), strides = (2, 2), activation = 'relu')(X)
    X = Conv2D(filters = 64, kernel_size = (3, 3), strides = (1, 1), activation = 'relu')(X)
    X = Conv2D(filters = 64, kernel_size = (3, 3), strides = (1, 1), activation = 'relu')(X)

    # Flattened layer
    X = Flatten()(X)

    # PilotNet first fully-connected layer + dropout
    X = Dense(units = 1152, activation = 'relu')(X)
    X = Dropout(rate = 0.1)(X)

    # PilotNet second fully-connected layer + dropout
    X = Dense(units = 100, activation = 'relu')(X)
    X = Dropout(rate = 0.1)(X)

    # PilotNet third fully-connected layer + dropout
    X = Dense(units = 50, activation = 'relu')(X)
    X = Dropout(rate = 0.1)(X)

    # PilotNet fourth fully-connected layer + dropout
    X = Dense(units = 10, activation = 'relu')(X)
    X = Dropout(rate = 0.1)(X)

    # Steering angle output - linear
    steering_out = Dense(units = 1, activation = 'linear')(X)
    #Scale the atan of steering output
    steering_out = Lambda(lambda x: tf.multiply(tf.atan(x), 2), name = 'steering_out')(steering_out)

    # Throttle output - linear
    throttle_out = Dense(units = 1, activation = 'linear')(X)
    # Scale the atan of throttle output
    throttle_out = Lambda(lambda x: tf.multiply(tf.atan(x), 2), name = 'throttle_out')(throttle_out)

    # Build and compile model
    model = Model(inputs = [input_shape], outputs = [steering_out, throttle_out])

    # Compile model for linear
    model.compile(optimizer=Adam(lr = 1e-4),
                  loss = {'steering_out': 'mse', 'throttle_out': 'mse'})


    return model