__author__ = 'mukundmk'

from flask import Flask
from flask.ext.login import LoginManager
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.mail import Mail
from flask.ext.socketio import SocketIO
from .neo4jclient import Neo4jClient

app = Flask(__name__)
app.config.from_pyfile('config.py')
lm = LoginManager(app)
lm.login_view = 'login'
db = SQLAlchemy(app)
mail = Mail(app)
socketio = SocketIO(app)
active_users = dict()
neo4jcli = Neo4jClient()

from app import views, models, events