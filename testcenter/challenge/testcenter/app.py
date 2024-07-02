from datetime import timedelta

from flask import Flask
from flask_login import LoginManager

import util.util
from auth import auth as auth_blueprint
from main import main as main_blueprint
from api import api as api_blueprint
from model import db
from model.Users import User
from model.TestResults import TestResult
from model.TrustedKeys import TrustedKey
import os

app = Flask(__name__)

app.config['SECRET_KEY'] = "WW91IHdpbGwgZm9yZXZlciBiZSBteSBhbHdheXMsIGJvbyA8MyE="
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"postgresql://{os.getenv('PG_User', 'postgres')}:"
    f"{os.getenv('PG_Password', 'postgres')}"
    f"@{os.getenv('PG_Host', '127.0.0.1')}:5432/"
    f"{os.getenv('PG_DB', 'test')}")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

    if not TrustedKey.query.all():
        with open("./res/csca.key", "rb") as f:
            private_key = f.read()

        with open("./res/csca.pem", "rb") as f:
            public_key = f.read()

        util.util.import_trusted_keys(public_key, private_key)
        TrustedKey.query.first().is_signup_key = True

    db.session.commit()

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = "warning"
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return User.query.get(int(user_id))


app.register_blueprint(main_blueprint)
app.register_blueprint(auth_blueprint)
app.register_blueprint(api_blueprint)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
