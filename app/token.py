__author__ = 'mukundmk'

from itsdangerous import URLSafeSerializer

from app import app


def generate_token(email):
    serializer = URLSafeSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=app.config['TOKEN_SALT'])


def verify_token(token):
    serializer = URLSafeSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt=app.config['TOKEN_SALT'])
    except:
        return False
    return email