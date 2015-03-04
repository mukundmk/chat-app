__author__ = 'mukundmk'

from app import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String(130), index=True)
    activated = db.Column(db.Boolean, index=True)
    status = db.Column(db.String(140), index=True)

    @staticmethod
    def is_authenticated():
        return True

    def is_active(self):
        return self.activated

    @staticmethod
    def is_anonymous():
        return False

    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return '<User %r>' % self.id
