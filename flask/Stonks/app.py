from flask import Flask, redirect, url_for, request, render_template, jsonify

from ./Stonks.schema import DB
from ./Stonks.functions.templatedb_builder import build_template_db
from ./Stonks.functions.google_imgdir_builder import build_google_imgdir
from ./Stonks.functions.imgdir_builder import build_imgdir
from ./Stonks.routes.demo_file import demo_file_bp
from ./Stonks.routes.demo_url import demo_url_bp


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

    app.config.from_object("Stonks.config.Config")

    DB.init_app(app)

    app.register_blueprint(demo_file_bp)
    app.register_blueprint(demo_url_bp)

    @app.route('/')
    def redir():
        return redirect(url_for('upload'))

    @app.route('/google_imgdir')
    def google_imgdir():
        return jsonify(build_google_imgdir())

    @app.route('/imgdir')
    def imgdir():
        return jsonify(build_imgdir())
    
    @app.route('/templates')
    def templates():
        return jsonify(build_template_db())


    @app.route('/reset')
    def reset():
        # DB.drop_all()
        DB.create_all()
        return redirect(url_for('upload'))
    
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