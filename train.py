import keras,os
from keras.models import Sequential
from keras.layers import Dense, Conv2D, MaxPool2D , Flatten
from keras.preprocessing.image import ImageDataGenerator
from keras.optimizers import Adam
from keras.callbacks import ModelCheckpoint, EarlyStopping
from Stonks.models.vgg16.architecture import get_blank_vgg16
from Stonks.functions.constants import IMGDIR_PATH
import numpy as np

img_height = 224
img_width = 224
batch_size = 32
weights_path = "vgg16_1.h5"

model = get_blank_vgg16()
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
    IMGDIR_PATH,
    target_size=(img_height, img_width),
    class_mode='binary',
    batch_size = 64,
    subset='training'
)

validation_generator = train_datagen.flow_from_directory(
    IMGDIR_PATH,
    target_size=(img_height, img_width),
    class_mode='binary',
    subset='validation'
)

compile_kwargs = {
    'optimizer': Adam(lr=0.001),
    'loss': keras.losses.sparse_categorical_crossentropy,
    'metrics': ['accuracy']
}
model.compile(**compile_kwargs)
checkpoint_kwargs = {
    'monitor': 'accuracy',
    'verbose': 1,
    'save_best_only': True,
    'save_weights_only': False,
    'mode': 'auto',
    'period': 1
}
checkpoint = ModelCheckpoint(weights_path, **checkpoint_kwargs)
early_stopping_kwargs = {
    'monitor': 'val_accuracy',
    'min_delta': 0,
    'patience': 20,
    'verbose': 1,
    'mode': 'auto'
}
early = EarlyStopping(**early_stopping_kwargs)
generator_kwargs = {
    'steps_per_epoch': 830,
    'generator': train_generator,
    'validation_data': validation_generator,
    'validation_steps': 83,
    'epochs': 100,
    'callbacks': [checkpoint,early]
}

if __name__ == "__main__":
    hist = model.fit_generator(**generator_kwargs)