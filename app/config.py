__author__ = 'mukundmk'

import os
basedir = os.path.abspath(os.path.dirname(__file__))

user_name = 'root'
passwd = 'toor'
host = 'localhost'
port = '3306'
database = 'chat_app'
SQLALCHEMY_DATABASE_URI = 'mysql://' + user_name + ':' + passwd + '@' + host + ':' + port + '/' + database

SECRET_KEY = '\x85\xb1df\x1e\xa8v\x9c\xf6\x0c=G\xf2x"\x91\x12\x9e\x8de\xc95Z-\x072/\t\x91\x87\xf8\x9a'
IV = '\xaf5\xeeO\x8a:F\xfe5\r\xac\x96:\x15\xa3\t'
TOKEN_SALT = '\xab\xfej\x7f-\x1b\xa0\x94\xae\xf8\x93\xa5\x9f\x82\x7f\x99\x90Vn(\x8c\xfa\x1d\xc8\x0b1Z\x9dc\x1bC<'

MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = 'todothelist@gmail.com'
MAIL_PASSWORD = 'thetodolist'
DEFAULT_MAIL_SENDER = 'Chat-App'

