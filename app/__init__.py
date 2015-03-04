__author__ = 'mukundmk'

import ssl

from flask import Flask
from flask.ext.login import LoginManager
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.mail import Mail

app = Flask(__name__)
app.config.from_pyfile('config.py')
lm = LoginManager(app)
lm.login_view = 'login'
db = SQLAlchemy(app)
mail = Mail(app)

print app.config['SERVER_NAME']

from app import views, models