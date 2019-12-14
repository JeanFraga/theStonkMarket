from flask import Blueprint, jsonify, request, render_template

import json, requests, os, io

from Stonks.classes.Input_Handler import Input_Handler
from PIL import Image

demo_file_bp = Blueprint('demo_file_bp', __name__)


@demo_file_bp.route('/demo_file', methods=['GET', 'POST'])
def demo_file():
    infile = request.files['file']
    data = Input_Handler().get_by_file(infile)

    return jsonify(data)
