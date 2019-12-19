from flask_script import Manager, Server

from Stonks.scripts.templatedb_builder import build_template_db
from Stonks.schema import DB
from Stonks.app import create_app

class MyFlaskApp(Flask):
  def run(self, **kwargs):
    with self.app_context():
        first_build_init()
    super(MyFlaskApp, self).run(**kwargs)

def on_app_init():
    DB.create_all()
    build_template_db()

class CustomServer(Server):
    def __call__(self, app, *args, **kwargs):
        on_app_init()
        return Server.__call__(self, app, *args, **kwargs)

def create_manager():
    manager = Manager(app=create_app())
    manager.add_command('runserver', CustomServer())
    return manager
