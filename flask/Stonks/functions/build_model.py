import os, keras
from keras import applications
from keras.models import Sequential, load_model
from keras.layers import Dense

from Stonks.functions.constants import DATASET_PATH

img_height = 224
img_width = 224
img_channel = 3

weights_path = "Stonks/models/template_clf.h5"

try: output_size = sum(os.path.isdir(os.path.join(DATASET_PATH, i)) for i in os.listdir(DATASET_PATH))
except: output_size = 807
stepdown_multiplier = 4

def create_model():
    vgg16 = applications.VGG16(
        weights='imagenet',
        input_shape=(img_height, img_width, img_channel)
    )

    model = Sequential()
    for layer in vgg16.layers[:-2]:
        model.add(layer)
    
    del vgg16

    model.add(Dense(units=stepdown_multiplier*output_size, activation="relu"))
    model.add(Dense(units=output_size, activation="softmax"))

    try:
        model.load_weights(weights_path)
    except: pass

    return model