__author__ = 'mukundmk'

import ssl

from flask import Flask
from flask.ext.login import LoginManager
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_pyfile('config.py')
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'
db = SQLAlchemy(app)

from app import views, models