__author__ = 'mukundmk'

import os
basedir = os.path.abspath(os.path.dirname(__file__))

user_name = ''
passwd = ''
host = 'localhost'
port = '3306'
database = 'chat_app'
SQLALCHEMY_DATABASE_URI = 'mysql://' + user_name + ':' + passwd + '@' + host + ':' + port + '/' + database

SECRET_KEY = ''
IV = ''
TOKEN_SALT = ''

MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = ''
MAIL_PASSWORD = ''
DEFAULT_MAIL_SENDER = 'Chat-App'

