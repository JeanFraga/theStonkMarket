import os
from decouple import config

from flask import Flask, redirect, url_for, flash, request, render_template, jsonify

from Stonks.schema import DB
from Stonks.routes.demo_file import demo_file_bp
from Stonks.routes.demo_url import demo_url_bp
from Stonks.config import BaseConfig
from Stonks.scripts.first_build_init import build_db
from Stonks.scripts.google_imgdir_builder import build_google_imgdir
from Stonks.classes.reddit_scrapper import RedditScrapper

def create_app():
    app = Flask(__name__)
    app.config.from_object(BaseConfig)

    DB.init_app(app)
    
    app.register_blueprint(demo_file_bp)
    app.register_blueprint(demo_url_bp)

    @app.route('/')
    def redir():
        return redirect(url_for('upload'))

    @app.route('/reset')
    def reset():
        return jsonify(build_db())

    @app.route('/reddit')
    def reddit():
        return jsonify(RedditScrapper('dankmemes').get_score_df())

    @app.route('/google')
    def google():
        return jsonify(build_google_imgdir())

    @app.route('/upload')
    def upload():
        return render_template('base.html')

    return app