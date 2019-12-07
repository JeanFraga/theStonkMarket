from flask import Blueprint, jsonify, request, render_template

import json, requests, os, io

from Stonks.classes.Input_Handler import Input_Handler
from PIL import Image

demo_url_bp = Blueprint('demo_url_bp', __name__)


@demo_url_bp.route('/demo_url', methods=['GET', 'POST'])
def demo_url():
    url = request.form.get('url')
    data = Input_Handler().get_by_url(url)

    return jsonify(data)

