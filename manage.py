from flask.cli import FlaskGroup

from Stonks import APP
from Stonks.schema import DB


cli = FlaskGroup(APP)


@cli.command("create_db")
def create_db():
    DB.drop_all()
    DB.create_all()
    DB.session.commit()


if __name__ == "__main__":
    cli()