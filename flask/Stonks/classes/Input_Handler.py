import io, os, hashlib, requests, json

import numpy as np

from decouple import config
from PIL import Image
from Stonks.schema import DB, Prediction
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from cv2 import cv2

# constants
TEMP_FOLDER = 'Stonks/assets/temp'
weights_path = "Stonks/models/template_clf.h5"

model = load_model(weights_path)

class Input_Handler:
    def __init__(self):
        pass

    def get_by_url(self, url):
        with requests.get(url) as response:
            raw = Image.open(io.BytesIO(response.content))

        return self.get_by_file(raw)

    def get_by_file(self, img):
        out = model.predict_generator(im)
        return out