from .app import create_app

#may require tinkering depending on how gunicron is set up

APP = create_app()
if __name__ == "__main__":
    APP.run(host="0.0.0.0", port=5000,debug=False)
