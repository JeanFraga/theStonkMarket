from .app import create_app
from waitress import serve

#may require tinkering depending on how gunicron is set up

APP = create_app()
if __name__ == "__main__":
    serve(APP, host="0.0.0.0", port=5000)
