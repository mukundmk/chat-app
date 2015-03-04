__author__ = 'mukundmk'

import os
basedir = os.path.abspath(os.path.dirname(__file__))

user_name = ''
passwd = ''
host = 'localhost'
port = '3306'
database = 'chat_app'
SECRET_KEY = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
SQLALCHEMY_DATABASE_URI = 'mysql://' + user_name + ':' + passwd + '@' + host + ':' + port + '/' + database

