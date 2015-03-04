__author__ = 'mukundmk'

from flask.ext.mail import Message
from app import app, mail


def send_email(to, subject, template):
    msg = Message(
        subject,
        recipients=[to],
        html=template,
        sender=app.config['DEFAULT_MAIL_SENDER']
    )
    mail.send(msg)