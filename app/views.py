__author__ = 'mukundmk'

import hashlib
import datetime

from flask.ext.login import login_required, login_user, logout_user, current_user
from flask import *

from app import app, db, lm
from .models import User
from .token import generate_token, verify_token
from .mail import send_email

@app.before_request
def before_request():
    g.user = current_user

@lm.user_loader
def load_user(userid):
    return User.query.get(int(userid))



@app.route('/login', methods=['GET', 'POST'])
def login():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('index'))
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if not user:
            return render_template('login.html', invalid="*Invalid Credentials")
        if not user.is_active():
            return render_template('login.html', invalid="*Email ID Not Confirmed")

        password = hashlib.sha512(request.form['password']).hexdigest()
        if password == user.password:
            if request.form.get('remember') == 'on':
                print 'remember'
                login_user(user, remember=True)
            else:
                print 'dont remember'
                login_user(user)
            g.user = user
            return redirect(url_for('index'))

        else:
            return render_template('login.html', invalid="*Invalid Credentials")

    else:
        return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('index'))
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if user:
            return render_template('register.html', invalid=True, register=True)
        user = User(name=request.form['name'],
                    email=request.form['email'],
                    password=hashlib.sha512(request.form['password']).hexdigest(),
                    activated=False,
                    status='')
        db.session.add(user)
        db.session.commit()
        token = generate_token(user.email)
        subject = 'Please Confirm Your Email Id'
        confirm_url = url_for('confirm_email', token=token, _external=True)
        msg = render_template('confirm.html', confirm_url=confirm_url,
                              time=str(datetime.datetime.now().replace(microsecond=0)))
        send_email(user.email, subject, msg)
        return redirect(url_for('index'))
    else:
        return render_template('register.html', register=True)

@app.route('/confirm/<token>')
def confirm_email(token):
    email = verify_token(token)
    if email:
        user = User.query.filter_by(email=email).first()
        if user:
            user.activated = True
            db.session.commit()
    return redirect(url_for('index'))

@app.route('/')
@login_required
def index():
    return render_template('index.html', name=g.user.name)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))