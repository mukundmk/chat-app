__author__ = 'mukundmk'

import hashlib
import datetime
import os.path
import base64
import random
import string

from flask.ext.login import login_required, login_user, logout_user, current_user
from flask import *
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.PublicKey import RSA

from app import app, db, lm, active_users, neo4jcli
from .models import User, KeyTable
from .token import generate_token, verify_token
from .mail import send_email


@app.before_request
def before_request():
    g.user = current_user


@lm.user_loader
def load_user(userid):
    return User.query.get(int(userid))

@lm.header_loader
def load_user_from_header(header_val):
    header_val = header_val.replace('Basic ', '', 1)
    try:
        header_val = base64.b64decode(header_val)
    except TypeError:
        pass
    return User.query.filter_by(api_key=header_val).first()


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
            key = PBKDF2(request.form['password'], app.config['SECRET_KEY'], count=10000).encode('hex')
            aes = AES.new(key, AES.MODE_CBC, IV=app.config['IV'])
            cyphertext = KeyTable.query.get(user.id).passphrase.decode('hex')
            passphrase = aes.decrypt(cyphertext)
            key2 = PBKDF2(passphrase, app.config['SECRET_KEY'], count=10000).encode('hex')
            aes = AES.new(key2, AES.MODE_CBC, IV=app.config['IV'])
            f = open('keys/'+str(user.id)+'_private.txt')
            session['privatekey'] = aes.decrypt(f.read()).rstrip('\x00')
            f.close()
            f = open('keys/'+str(user.id)+'_public.txt')
            session['publickey'] = aes.decrypt(f.read()).rstrip('\x00')
            f.close()
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
        api_key = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.ascii_lowercase + string.digits)
                          for _ in range(32))
        user = User(name=request.form['name'],
                    email=request.form['email'],
                    password=hashlib.sha512(request.form['password']).hexdigest(),
                    activated=False,
                    status='',
                    api_key=api_key)
        db.session.add(user)
        db.session.commit()
        token = generate_token(user.email)
        subject = 'Please Confirm Your Email Id'
        confirm_url = url_for('confirm_email', token=token, _external=True)
        msg = render_template('confirm.html', confirm_url=confirm_url,
                              time=str(datetime.datetime.now().replace(microsecond=0)))
        neo4jcli.add_user(user.id)
        key = PBKDF2(request.form['password'], app.config['SECRET_KEY'], count=10000).encode('hex')
        passphrase = os.urandom(32)
        aes = AES.new(key, AES.MODE_CBC, IV=app.config['IV'])
        cyphertext = aes.encrypt(passphrase)
        encrypted_key = KeyTable(id=user.id, passphrase=cyphertext.encode('hex'))
        db.session.add(encrypted_key)
        db.session.commit()
        key2 = PBKDF2(passphrase, app.config['SECRET_KEY'], count=10000).encode('hex')
        aes = AES.new(key2, AES.MODE_CBC, IV=app.config['IV'])
        new_key = RSA.generate(1024, e=65537)
        private_key = new_key.exportKey('PEM')
        l = 16 - (len(private_key) % 16)
        private_key += '\x00' * l
        f = open('keys/'+str(user.id)+'_private.txt', 'w')
        f.write(aes.encrypt(private_key))
        f.close()
        public_key = new_key.publickey().exportKey('PEM')
        l = 16 - (len(public_key) % 16)
        public_key += '\x00' * l
        f = open('keys/'+str(user.id)+'_public.txt', 'w')
        f.write(aes.encrypt(public_key))
        f.close()
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
    add, friends = neo4jcli.get_added_user(g.user.id)
    users = list()
    added = list()
    for friend in friends:
        user = User.query.get(int(friend))
        data = dict()
        data['id'] = str(user.id)
        data['name'] = str(user.name)
        users.append(data)

    for toadd in add:
        user = User.query.get(int(toadd))
        data = dict()
        data['id'] = str(user.id)
        data['name'] = str(user.name)
        added.append(data)

    users.sort(key=lambda item: item['name'])
    added.sort(key=lambda item: item['name'])
    return render_template('index.html', name=g.user.name, userid=g.user.id, users=users, added=added)


@app.route('/logout')
@login_required
def logout():
    active_users[str(current_user.id)] = False
    logout_user()
    return redirect(url_for('index'))


@app.route('/get_online')
@login_required
def get_online():
    friends = neo4jcli.get_friends(g.user.id)
    active = dict()
    for friend in friends:
        active[friend] = active_users.get(friend, False)
    return json.dumps(active)


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
        for i in range(len(data)//3):
            response['data'].append([data[3*i].decode('string_escape').strip(),
                                     data[(3*i)+1].decode('string_escape').strip(),
                                     data[(3*i)+2].decode('string_escape').strip()])
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
    user = User.query.get(int(request.args['id']))
    if user:
        response = dict()
        response['id'] = user.id
        response['name'] = user.name
        response['email'] = user.email
        response['status'] = user.status
        response['friendship'] = "2"
        if not neo4jcli.is_friend_of(str(g.user.id), response['id']):
            if not neo4jcli.is_friend_of(response['id'], str(g.user.id)):
                response['friendship'] = "0"
            else:
                response['friendship'] = "1"
        return json.dumps(response)
    else:
        return 'bad request', 400


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


@app.route('/search_user')
@login_required
def search_user():
    users = User.query.filter(User.name.like(request.args.get('query')+'%')).all()
    data = list()
    for i in users:
        if i.id == g.user.id:
            continue
        user = dict()
        user['value'] = str(i.id)
        user['label'] = str(i.name)
        data.append(user)
    data.sort(key=lambda item: item['label'])
    return json.dumps(data)


@app.route('/add_friend', methods=['POST'])
@login_required
def add_friend():
    user_id = request.form.get('id')
    neo4jcli.add_friend(g.user.id, user_id)
    add, friends = neo4jcli.get_added_user(g.user.id)
    added = list()
    users = list()

    for friend in friends:
        user = User.query.get(int(friend))
        data = dict()
        data['id'] = str(user.id)
        data['name'] = str(user.name)
        users.append(data)

    for toadd in add:
        user = User.query.get(int(toadd))
        data = dict()
        data['id'] = str(user.id)
        data['name'] = str(user.name)
        added.append(data)

    users.sort(key=lambda item: item['name'])
    added.sort(key=lambda item: item['name'])
    return json.dumps({'users': users, 'added': added})


@app.route('/decline_friend', methods=['POST'])
@login_required
def decline_friend():
    user_id = request.form.get('id')
    neo4jcli.decline_friend(user_id, g.user.id)
    add, friends = neo4jcli.get_added_user(g.user.id)
    added = list()

    for toadd in add:
        user = User.query.get(int(toadd))
        data = dict()
        data['id'] = str(user.id)
        data['name'] = str(user.name)
        added.append(data)

    added.sort(key=lambda item: item['name'])
    return json.dumps(added)


@app.route('/get_keys')
@login_required
def get_keys():
    return json.dumps({'privatekey': session.get('privatekey'), 'publickey': session.get('publickey')})


@app.route('/update_publickey', methods=['POST'])
@login_required
def update_publickey():
    key = KeyTable.query.get(g.user.id)
    if key.publickey != request.form.get('publickey'):
        key.publickey = request.form.get('publickey')
        db.session.commit()
    return 'Success'


@app.route('/get_publickey')
@login_required
def get_publickey():
    key = KeyTable.query.get(int(request.args.get('id')))
    if key:
        return json.dumps({'id': request.args.get('id'), 'key': key.publickey})
    else:
        return 'bad request', 400


@app.route('/get_media_file')
@login_required
def get_media_file():
    if os.path.isfile('messages/media_'+request.args.get('id')+'.txt'):
        f = open('messages/media_'+request.args.get('id')+'.txt')
        return f.read()
    else:
        return 'File Not Found', 404

@app.route('/apikey', methods=['POST'])
def get_apikey():
    email = request.form.get('email')
    passwd = request.form.get('password')
    if not email or not passwd:
        return json.dumps({'error': 'invalid credentials'})
    user = User.query.filter_by(email=email).first()
    if not user:
        return json.dumps({'error': 'invalid credentials'})
    if not user.is_active():
        return json.dumps({'error': 'invalid credentials'})
    password = hashlib.sha512(passwd).hexdigest()
    if password != user.password:
        return json.dumps({'error': 'invalid credentials'})
    response_data = dict()
    response_data['apikey'] = base64.b64encode(user.api_key)
    key = PBKDF2(passwd, app.config['SECRET_KEY'], count=10000).encode('hex')
    aes = AES.new(key, AES.MODE_CBC, IV=app.config['IV'])
    cyphertext = KeyTable.query.get(user.id).passphrase.decode('hex')
    passphrase = aes.decrypt(cyphertext)
    key2 = PBKDF2(passphrase, app.config['SECRET_KEY'], count=10000).encode('hex')
    aes = AES.new(key2, AES.MODE_CBC, IV=app.config['IV'])
    f = open('keys/'+str(user.id)+'_private.txt')
    response_data['privatekey'] = aes.decrypt(f.read()).rstrip('\x00')
    f.close()
    f = open('keys/'+str(user.id)+'_public.txt')
    response_data['publickey'] = aes.decrypt(f.read()).rstrip('\x00')
    f.close()
    return json.dumps(response_data)