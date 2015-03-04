__author__ = 'mukundmk'

import hashlib

from flask.ext.login import login_required, login_user, logout_user, current_user
from flask import *

from app import app, db, lm
from .models import User


@app.before_request
def before_request():
    g.user = current_user

@lm.user_loader
def load_user(userid):
    print User.query.get(userid)
    return User.query.get(userid)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('index'))
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if not user:
            return render_template('login.html', invalid=True)

        password = hashlib.sha512(request.form['password']).hexdigest()
        if password == user.password:
            if request.form.get('remember') == 'on':
                login_user(user, remember=True)
            else:
                login_user(user)
            g.user = user
            return redirect(url_for('index'))

        else:
            return render_template('login.html', invalid=True)

    else:
        return render_template('login.html')

@app.route('/register', methods=['GET','POST'])
def register():
    #TODO: Email Verification
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('index'))
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if user:
            return render_template('register.html', invalid=True, register=True)
        user = User(
                    name=request.form['name'],
                    email=request.form['email'],
                    password=hashlib.sha512(request.form['password']).hexdigest())
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('index'))
    else:
        return render_template('register.html', register=True)

@app.route('/')
@login_required
def index():
    return render_template('index.html', name=g.user.name)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))