from .app import create_app
from waitress import serve

APP = create_app()

# serve(APP, host="0.0.0.0", port=5000)
