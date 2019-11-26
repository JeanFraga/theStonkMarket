import io
import os
import hashlib
import requests
import json
from decouple import config
from werkzeug.utils import secure_filename
import boto3, botocore

from PIL import Image
from Stonks.schema import DB, HashTable
from shutil import copystat

# constants
IMGDIR_PATH = 'Stonks/assets/temp'
UPLOAD_FOLDER = 'Stonks/assets/temp/'
ExtraArgs = json.loads(config('ExtraArgs'))

# instantiate S3
AWS = {
    'aws_access_key_id': config('S3_KEY'),
    'aws_secret_access_key': config('S3_SECRET')
}
s3 = boto3.client("s3", **AWS)

def upload_file_to_s3(*args):
    try: s3.upload_fileobj(*args, ExtraArgs=ExtraArgs)
    except Exception as e: return str(e)
    return "{}{}".format(config('S3_LOCATION'), args[2])

def is_dup(file_hash:str, model_list:list) -> dict:
    """Checks if the image has been processed before
    
    Arguments:
        file_hash {string} -- [md5 hash of image]
    
    Returns:
        [dict] -- [returns a empty dict if not a dup, returns stored data if is a dup]
    """
    data = {'hash': file_hash}
    is_img_dup = HashTable.query.filter(HashTable.hash == file_hash).all()
    if is_img_dup:
        for model in model_list:
            if model.__name__ != 'faces':
                data[model.__name__] = getattr(is_img_dup[0], model.__name__)
        data['hash'] = is_img_dup[0].hash
        data['faces_source'] = is_img_dup[0].faces_source
        data['yolov3_source'] = is_img_dup[0].yolov3_source
        data['original'] = is_img_dup[0].original
        data['error'] = ""
        return data
    else: return {}

class Input_Handler:
    """ Class that handles processing images
    
    Returns:
        [dict] -- [data from processing image]
    """
    def __init__(self, img_file, model_list: list):
        """ Takes in a img from hmtl form input of type and name file
        Also takes a list of the models to use but its hard coded in route atm

        gets hash of image to use as filename
        move file cursor back to 0
        upload to S3
        gets img from S3 to have desired format
        
        Arguments:
            img_file {blob} -- [contains image n metadata]
            model_list {list} -- [list of the model objects]
        """
        self.model_list = model_list
        self.img_file = img_file
        self.hash = hashlib.md5(img_file.read()).hexdigest()
        self.img_file.seek(0)
        self.img_url = upload_file_to_s3(self.img_file, config('S3_BUCKET'), self.hash+'.png')
        self.img_file = requests.get(self.img_url).content

    def get_pred_data(self) -> dict:
        """builds the prediction data in a dictionary
        
        instantiate dict to store prediction data
        check if this image have ben processed before
        construct outpput file name
        save image locally with pillow as png
        run loop over model list
        run model on image
        extract url in model return and put back in at correct place
        delete empty model returns
        dump to string if not empty
        add data to database
        clear files in temp folder
        create placeholder file in folder for git purposes
        add that there wasnt an error to data dict

        Returns:
            dict -- [the reponse data]
        """
        data = {'original': self.img_url, 'hash': self.hash}
        
        is_img_dup = is_dup(data['hash'], self.model_list)
        if is_img_dup: return is_img_dup

        output_filename = os.path.join(IMGDIR_PATH, f"{data['hash']}.png")
        
        with open(output_filename, 'wb') as out_file:
            Image.open(io.BytesIO(requests.get(self.img_url).content)).save(out_file, format='png')
  
        for model in self.model_list:
            data[model.__name__] = model(output_filename)

            if 'url' in data[model.__name__]:
                data[model.__name__+'_source'] = data[model.__name__]['url']
                del data[model.__name__]['url']
            if data[model.__name__]: data[model.__name__] = json.dumps(data[model.__name__])
            else: del data[model.__name__]
   
        DB.session.add(HashTable(**data))
        DB.session.commit()

        for model in self.model_list:
            if model.__name__ != 'faces': data[model.__name__] = json.loads(data[model.__name__])

        for filename in os.listdir(IMGDIR_PATH):
            os.remove(os.path.join(IMGDIR_PATH, filename))
        
        with open(os.path.join(IMGDIR_PATH, 'placeholder.py'), 'wb'):
            data['error'] = ""

        return data