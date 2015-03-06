__author__ = 'mukundmk'

import hashlib
import datetime
import os.path

from flask.ext.login import login_required, login_user, logout_user, current_user
from flask import *

from app import app, db, lm, active_users
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
                login_user(user, remember=True)
            else:
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
    active_users[str(current_user.id)] = True
    users = list()
    for user in User.query.filter_by().order_by(User.name):
        if user.id == g.user.id:
            continue
        data = dict()
        data['id'] = str(user.id)
        data['name'] = str(user.name)
        users.append(data)
    print users
    return render_template('index.html', name=g.user.name, userid=g.user.id, users=users)


@app.route('/logout')
@login_required
def logout():
    active_users[str(current_user.id)] = False
    logout_user()
    return redirect(url_for('index'))


@app.route('/get_online')
@login_required
def get_online():
    return json.dumps(active_users)


@app.route('/get_user')
@login_required
def get_user():
    response = dict()
    response['id'] = str(g.user.id)
    response['name'] = str(g.user.name)
    return json.dumps(response)


@app.route('/get_image')
@login_required
def get_image():
    uid = request.args.get('id')
    print uid
    if os.path.isfile('app/static/images/'+uid+'.png'):
        return send_file('static/images/'+uid+'.png', mimetype='image/png')
    elif os.path.isfile('app/static/images/'+uid+'.jpg'):
        return send_file('static/images/'+uid+'.jpg', mimetype='image/jpeg')
    else:
        return send_file('static/images/default.png', mimetype='image/png')


@app.route('/get_messages')
@login_required
def get_messages():
    response = dict()
    response['id1'] = str(g.user.id)
    response['id2'] = str(request.args.get('id', ''))
    response['data'] = []
    if os.path.isfile('messages/'+response['id1']+'_'+response['id2']+'.txt'):
        f = open('messages/'+response['id1']+'_'+response['id2']+'.txt')
        data = f.readlines()
        for i in range(len(data)//2):
            response['data'].append([data[2*i].decode('string_escape').strip(),
                                     data[(2*i)+1].decode('string_escape').strip()])
    print response
    return json.dumps(response)


@app.route('/get_profile')
@login_required
def get_profile():
    user = dict()
    user['id'] = str(g.user.id)
    user['name'] = str(g.user.name)
    user['email'] = str(g.user.email)
    user['status'] = str(g.user.status)
    return render_template('profile.html', user=user)


@app.route('/profile_of')
@login_required
def profile_of():
    user = User.query.get(int(request.args["id"]))
    if user:
        response = dict()
        response["id"] = user.id
        response["name"] = user.name
        response["email"] = user.email
        response["status"] = user.status
        return json.dumps(response)
    else:
        return "bad request", 400


@app.route('/edit_profile', methods=['POST'])
@login_required
def edit_profile():
    if request.form['key'] == 'name':
        g.user.name = request.form['value']
    if request.form['key'] == 'status':
        g.user.status = request.form['value']
    db.session.commit()
    return request.form['key']+':'+request.form['value']


@app.route('/upload_image', methods=['POST'])
@login_required
def upload_image():
    img_file = request.files['file']
    if img_file.mimetype == 'image/png':
        if os.path.isfile('app/static/images/'+str(g.user.id)+'.jpg'):
            os.remove('app/static/images/'+str(g.user.id)+'.jpg')
        f = open('app/static/images/'+str(g.user.id)+'.png', 'w')
    elif img_file.mimetype == 'image/jpeg':
        if os.path.isfile('app/static/images/'+str(g.user.id)+'.png'):
            os.remove('app/static/images/'+str(g.user.id)+'.png')
        f = open('app/static/images/'+str(g.user.id)+'.jpg', 'w')
    else:
        return 'bad request', 400

    img_file.save(f)
    f.close()
    return str(g.user.id)