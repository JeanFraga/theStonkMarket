from flask import Flask, redirect, url_for, flash, request, render_template, jsonify

from Stonks.schema import DB
from Stonks.functions.train_data_builder import build_template_db


from flask_cors import CORS
import os
from decouple import config
from dotenv import load_dotenv

load_dotenv()

path = os.getcwd()
path = path + '/'
logpath = 'nohup.out'
logfile = path + logpath

def create_app():
    app = Flask(__name__)
    CORS(app)

    app.config['SQLALCHEMY_DATABASE_URI'] = config('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    DB.init_app(app)

    @app.route('/')
    def redir():
        return redirect(url_for('reset'))
    
    @app.route('/templates')
    def templates():
        return jsonify(build_template_db())


    @app.route('/reset')
    def reset():
        DB.drop_all()
        DB.create_all()
        return redirect(url_for('templates'))
    
    @app.route('/upload')
    def upload():
        return render_template('base.html')
    
    @app.route('/log')
    def log():
        with open(logpath, 'r') as logfile:
            cleanlog = logfile.read()
            cleanlog = cleanlog.replace("\ ", "\n")
            return render_template('log.html',log=cleanlog)

    return app