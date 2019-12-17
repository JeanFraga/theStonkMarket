import io, os, hashlib, requests, json, shutil
import numpy as np
from decouple import config
from PIL import Image
from cv2 import cv2

from Stonks.schema import DB, Template
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from os.path import join, dirname

# constants
PRED_GEN_DIR = 'pred_gen_dir'
weights_path = "Stonks/models/template_clf.h5"

def to_hash(img):
   return hashlib.md5(img.tobytes()).hexdigest()

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

class Input_Handler:
    def __init__(self):
        pass

    def get_by_url(self, url):
        with requests.get(url) as response:
            img = Image.open(io.BytesIO(response.content))

        PRED_GEN_FOLDER = join(PRED_GEN_DIR, f'{to_hash(img)}')
        os.makedirs(join(PRED_GEN_FOLDER, 'temp'))
        img.save(join(PRED_GEN_FOLDER, 'temp/temp.png'), format='png')

        PRED_GEN = ImageDataGenerator().flow_from_directory(
            PRED_GEN_FOLDER,
            target_size=(img_height, img_width),
            color_mode="rgb",
        )

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

        # templates = DB.session.query(Template).all()
        # names = [template.name for template in templates]   
        # out = names[np.argmax(model.predict_generator(PRED_GEN)[0])]
        out = np.argmax(model.predict_generator(PRED_GEN)[0])
        shutil.rmtree(PRED_GEN_FOLDER)


        return str(out)

    def get_by_file(self):
        out = model.predict_generator(PRED_GEN)
        return out