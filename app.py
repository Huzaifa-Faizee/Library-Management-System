from flask import Flask
from application.database import db
app = None
from flask_session import Session


def create_app():
    app = Flask(__name__)
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///library_management_system.db"
    db.init_app(app)
    app.app_context().push()
    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_TYPE"] = "filesystem"
    Session(app)

    return app


app = create_app()

from application.controllers import *

if __name__ == "__main__":
    # app.debug == True
    app.run()
