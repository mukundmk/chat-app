__author__ = 'mukundmk'

import os
basedir = os.path.abspath(os.path.dirname(__file__))

user_name = 'root'
passwd = 'toor'
host = 'localhost'
port = '3306'
database = 'chat_app'
SECRET_KEY = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
SQLALCHEMY_DATABASE_URI = 'mysql://' + user_name + ':' + passwd + '@' + host + ':' + port + '/' + database

GOOGLE_LOGIN_CLIENT_ID = '150588492556-gfu3h9qq7076jc6pvbdhkm3bqun23mds.apps.googleusercontent.com'
GOOGLE_LOGIN_CLIENT_SECRET = 'PHjTGlr_Ql4DV3819GNy5508'
GOOGLE_LOGIN_REDIRECT_URI = 'http://localhost:5000/oauth2callback'