from flask_sqlalchemy import SQLAlchemy

DB = SQLAlchemy()

class HashTable(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    original = DB.Column(DB.String(200), nullable=False)
    yolov3_source = DB.Column(DB.String(200), nullable=False)
    faces_source = DB.Column(DB.String(200), nullable=False)
    hash = DB.Column(DB.String(50), nullable=False)
    resnet = DB.Column(DB.String(500))
    yolov3 = DB.Column(DB.String(500))

class Template(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    name = DB.Column(DB.String(200), nullable=False)
    url = DB.Column(DB.String(200), nullable=False)
    imgflip_page = DB.Column(DB.String(200), nullable=False)
    filename = DB.Column(DB.String(200))

class Prediction(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    url = DB.Column(DB.String(200))
    filename = DB.Column(DB.String(200))
    hash = DB.Column(DB.String(200), nullable=False)

    pred = DB.Column(DB.Integer, DB.ForeignKey('template.name'), nullable=False)
    template = DB.relationship('Template', backref=DB.backref('preds', lazy=True))