import keras, os
from keras import applications
from keras.models import Sequential, load_model
from keras.models import load_model
from keras.layers import Dense, Conv2D, MaxPool2D , Flatten, Dropout
from keras.preprocessing.image import ImageDataGenerator
from keras.optimizers import SGD
from keras.callbacks import ModelCheckpoint, EarlyStopping

from Stonks.functions.constants import DATASET_PATH
from Stonks.functions.build_model import create_model, img_height, img_width, img_channel, weights_path
import numpy as np
import matplotlib.pyplot as plt

import tensorflow as tf


"""

Constants

"""

batch_size = 32
patience = 20

epochs = 64_000 // batch_size
steps_per_epoch = 32_000 // batch_size
validation_steps = 3_200 // batch_size

optimizer_kwargs = {
    'lr': 0.001,
    'clipnorm': 1.,
    'momentum': 0.9,
    'decay': 0.,
    'nesterov': True
}


def plot_model_results(hist):
    plt.plot(hist.history["categorical_accuracy"])
    plt.plot(hist.history['val_acc'])
    plt.plot(hist.history['loss'])
    plt.plot(hist.history['val_loss'])
    plt.title("Model Accuracy")
    plt.ylabel("Accuracy")
    plt.xlabel("Epoch")
    plt.legend(["Accuracy","Validation Accuracy","loss","Validation Loss"])
    plt.show()

if __name__ == "__main__":
    config = tf.ConfigProto()
    config.gpu_options.allow_growth=True
    sess = tf.Session(config=config)
    
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        validation_split=0.2
    )

    train_generator = train_datagen.flow_from_directory(
        DATASET_PATH,
        target_size=(img_height, img_width),
        class_mode='categorical',
        color_mode="rgb",
        subset='training',
        shuffle=True,
        seed=42
    )

    validation_generator = train_datagen.flow_from_directory(
        DATASET_PATH,
        target_size=(img_height, img_width),
        class_mode='categorical',
        color_mode="rgb",
        subset='validation',
        shuffle=True,
        seed=42
    )

    checkpoint = ModelCheckpoint(
        weights_path,
        monitor = 'categorical_accuracy',
        verbose = 1,
        save_best_only = True,
        save_weights_only = False,
        mode = 'auto',
        period = 1
    )
    early = EarlyStopping(
        monitor = 'categorical_accuracy',
        min_delta = 0,
        patience = patience,
        verbose = 1,
        mode = 'auto'
    )
    model = create_model()

    for layer in model.layers[:-11]:
        layer.trainable = False

    model.compile(
        optimizer = SGD(**optimizer_kwargs),
        loss = keras.losses.categorical_crossentropy,
        metrics = ['categorical_accuracy'] 
    )
    hist = model.fit_generator(
        steps_per_epoch = steps_per_epoch,
        generator = train_generator,
        validation_data = validation_generator,
        validation_steps = validation_steps,
        epochs = epochs,
        callbacks = [checkpoint, early]
    )
    
    plot_model_results(hist)