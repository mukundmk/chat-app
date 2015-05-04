__author__ = 'mukundmk'

from flask.ext.socketio import join_room, emit
from flask.ext.login import current_user

from app import socketio, active_users

from flask import request

import functools
import json


def authenticated_only(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated():
            request.namespace.disconnect()
        else:
            return f(*args, **kwargs)
    return wrapped


@socketio.on('connect', namespace='/chat')
def connect():
    print "connected"
    emit('join room req', "hello")

@socketio.on('join room', namespace='/chat')
def joinroom(message):
    print message['id']
    join_room(message['id'])
    msg = dict()
    msg['message'] = 'User connected'
    msg['userid'] = message['id']
    print str(message['id']) + ' connected'

@socketio.on('disconnect', namespace='/chat')
def disconnect():
    print 'disconnected'


@socketio.on('send message', namespace='/chat')
def send_message(message):
    print 'recieved'
    msg = dict()
    msg['from'] = message.get('from', '')
    msg['to'] = message.get('to', '')
    msg['type'] = message.get('type', '')
    msg['data'] = message.get('data', '')
    msg['aes_key'] = message.get('key_1', '')
    key_2 = message.get('key_2', '')
    if msg['type'] != 'text':
        data = dict()
        data['ciphertext'] = msg['data']
        data[msg['from']] = key_2
        data[msg['to']] = msg['aes_key']
        f = open('messages/count.txt')
        count = int(f.readline())
        f.close()
        f = open('messages/media_'+str(count)+'.txt', 'w')
        f.write(json.dumps(data))
        msg['data'] = str(count)
        f.close()
        count += 1
        f = open('messages/count.txt', 'w')
        f.write(str(count))
        f.close()
    f = open('messages/'+msg['to']+'_'+msg['from']+'.txt', 'a')
    f.write(str(msg['from']) + '\n' + str(msg['type']) + '\n' + str(str(msg['data']).encode('string_escape'))+'\n' +
            str(str(msg['aes_key'])+'\n').encode('string_escape')+'\n')
    f.close()
    f = open('messages/'+msg['from']+'_'+msg['to']+'.txt', 'a')
    f.write(str(msg['from']) + '\n' + str(msg['type']) + '\n' + str(str(msg['data']).encode('string_escape'))+'\n' +
            str(str(key_2).encode('string_escape'))+'\n')
    f.close()
    if active_users.get(str(message.get('to', '')), False):
        emit('receive message', msg, room=str(msg['to']))
    else:
        emit('error', {'message': 'User Offline'})
