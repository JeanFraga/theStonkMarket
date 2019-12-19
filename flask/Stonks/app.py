import os
from decouple import config
from dotenv import load_dotenv

from flask import Flask, redirect, url_for, flash, request, render_template, jsonify

from schema import DB
from routes.demo_file import demo_file_bp
from routes.demo_url import demo_url_bp
from config import BaseConfig

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config.from_object(BaseConfig)

    with app.app_context():
        DB.init_app(app)

    app.app_context().push()
    app.register_blueprint(demo_file_bp)
    app.register_blueprint(demo_url_bp)

    @app.route('/')
    def redir():
        return redirect(url_for('upload'))

    @app.route('/upload')
    def upload():
        return render_template('base.html')

    return app