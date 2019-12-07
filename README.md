# Pic Metric 3 - Data Science API
## Authors
* Rob Hamilton DS7 @Rob1Ham
* Anthony Hart DS7
* Jeremy Meek DS8
* David Hang DS8

* Instructor & Advisor - Jon Cody Sokol

Built on Deep Learning AMI (Amazon Linux) Version 25.3 - ami-028a41f747ffea9c0 using a g4dn.xlarge ec2 instance.

## Setup

Upon loading the server run the bootstrap.sh file, then create the .ev file.
Reference .env file, place in the Repo folder:

```
FLASK_ENV='development'
FLASK_APP='Stonks:APP'

DATABASE_URL='postgres://Username:Password@URL:5432/table'

S3_KEY = 'KEYGOESHERE'
S3_SECRET = 'SECRETGOESHERE'
S3_BUCKET = 'BUCKETGOESHERE'
S3_LOCATION = 'http://BUCKETNAME.s3.amazonaws.com/'

ExtraArgs='{"ACL": "public-read", "ContentType": "image/png", "ContentDisposition": "inline"}'
```

To run the app, go into the Repo folder and run
```
source activate tensorflow_p36
gunicorn -t 120 "Stonks:create_app()"
```


## Models
* Res Net 50 - Trained on 1,000 classes in object recognition!
* Yolo_V3 Coco - "You Only Look Once" - Trained on 80 classes in object recognition, and idenifies bounding boxes for objects are in the images 
* MTCNN - Multi-task Cascaded Convolutional Neural Networks for Face Detection. Trained on faces, and draws where the Neural Network identifies faces and where eyes/mouth/nose are located.

## Use


With the Flask App running, you are able to use the `:5000/upload` path to verify both uploaded images and posted URLS will work.


Lets use a test image:


### Original Image
![Original](http://Stonks3.s3.amazonaws.com/4f055f233ff79efdb5fdd377b2161c45.png)



It will take ~30 seconds to churn through all the Neural Networks, when completed a response JSON is returned:


``` javascript
{
  "error": "",
  "faces_source": "http://Stonks3.s3.amazonaws.com/c19b284ae9180e15d537ffe66ddebf8d_faces.png",
  "hash": "4f055f233ff79efdb5fdd377b2161c45",
  "original": "http://Stonks3.s3.amazonaws.com/4f055f233ff79efdb5fdd377b2161c45.png",
  "resnet": "{\"studio_couch\": \"0.7868622\", \"library\": \"0.055205315\", \"window_shade\": \"0.024714082\"}",
  "yolov3": "{\"potted plant\": \"67.16461777687073\", \"couch\": \"95.92761397361755\", \"person\": \"99.80075359344482\"}",
  "yolov3_source": "http://Stonks3.s3.amazonaws.com/c19b284ae9180e15d537ffe66ddebf8d_yolov3.png"
}
```
* error catches = (some) errors on the server
* faces_source = S3 Path drawing the facial identification shared from the MCTNN
* hash = md5 hash of the original uploaded image - used to prevent duplicate photos from being processed
* original = original image sent via upload or link, but hosted in s3!
* resnet = The objects detected, and the percent certainty it was detected in the photo.
* yolov3 = What objects were detected in the image according to yolov3, and percent certainty of the prediction.
* yolov3_source = The bounding boxes identified by yolov3


###  Yolo_v3 "You Only Look Once" - analyzed Image: 
![Yolo](http://Stonks3.s3.amazonaws.com/c19b284ae9180e15d537ffe66ddebf8d_yolov3.png)


### MTCNN - Facial Recognition - analyzed Image:
![MTCNN](http://Stonks3.s3.amazonaws.com/c19b284ae9180e15d537ffe66ddebf8d_faces.png)

## Routing
* All running on Port 5000 (Flask App default)
* `/reset` will reset and reinitiate the database
* `/upload` will take you to the upload form
* `/do_data_science` is the route for processing images via POST request
* `/do_data_science_url` is the route for processing URLs via POST request
* `/log` is the route to load the nohup.out file for quick checking of Back End of Flask Logs

## To Do

* Optimize time to return images, parrelizing jobs either within the flask app or by distributing across AWS Sagemaker.
* standardize sizing and file formats using PIL for hosted iamges.


