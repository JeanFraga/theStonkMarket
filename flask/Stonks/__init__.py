from .app import create_app

APP = create_app()
APP.app_context().push()