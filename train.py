import keras, os
from keras import applications
from keras.models import Sequential, Model, load_model
from keras.models import load_model
from keras.layers import Dense, Conv2D, MaxPool2D , Flatten, Dropout, Dense
from keras.preprocessing.image import ImageDataGenerator
from keras.optimizers import Adam
from keras.callbacks import ModelCheckpoint, EarlyStopping

from Stonks.functions.constants import DATASET_PATH
import numpy as np
import matplotlib.pyplot as plt

img_height = 224
img_width = 224
img_channel = 3
output_size = 10
batch_size = 32
weights_path = f"Stonks/models/template_clf_{output_size}.h5"

patience = 50
epochs = 64_000 // batch_size
steps_per_epoch = 32_000 // batch_size
validation_steps = 3_200 // batch_size

optimizer_kwargs = {
    'lr': 0.001,
    'clipnorm': 1.,
    'momentum': 0.9,
    'decay': 0.000001,
    'nesterov': False
}

vgg16 = applications.VGG16(weights='imagenet', input_shape=(img_height, img_width, img_channel))

model = Sequential()
for layer in vgg16.layers:
    model.add(layer)

model.layers.pop()
model.add(Dense(units=output_size, activation="softmax"))

try:
    model.load_weights(weights_path)
except: pass

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

compile_kwargs = {
    'optimizer': keras.optimizers.SGD(**optimizer_kwargs),
    'loss': keras.losses.categorical_crossentropy,
    'metrics': ['categorical_accuracy'] 
}
model.compile(**compile_kwargs)
checkpoint_kwargs = {
    'monitor': 'categorical_accuracy',
    'verbose': 1,
    'save_best_only': True,
    'save_weights_only': False,
    'mode': 'auto',
    'period': 1
}
checkpoint = ModelCheckpoint(weights_path, **checkpoint_kwargs)
early_stopping_kwargs = {
    'monitor': 'categorical_accuracy',
    'min_delta': 0,
    'patience': patience,
    'verbose': 1,
    'mode': 'auto'
}
early = EarlyStopping(**early_stopping_kwargs)
generator_kwargs = {
    'steps_per_epoch': steps_per_epoch,
    'generator': train_generator,
    'validation_data': validation_generator,
    'validation_steps': validation_steps,
    'epochs': epochs,
    'callbacks': [checkpoint,early]
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
    hist = model.fit_generator(**generator_kwargs)
    
    plot_model_results(hist)