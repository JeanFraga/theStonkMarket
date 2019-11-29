from flask_sqlalchemy import SQLAlchemy

DB = SQLAlchemy()

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