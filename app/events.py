__author__ = 'mukundmk'

from flask.ext.socketio import join_room, emit
from flask.ext.login import current_user

from app import socketio, active_users

from flask import request

import functools


def authenticated_only(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated():
            request.namespace.disconnect()
        else:
            return f(*args, **kwargs)
    return wrapped


@socketio.on('connect', namespace='/chat')
@authenticated_only
def connect():
    join_room(str(current_user.id))
    msg = dict()
    msg['message'] = 'User connected'
    msg['userid'] = str(current_user.id)
    print str(current_user.id) + ' connected'
    emit('connect', msg)


@socketio.on('disconnect', namespace='/chat')
@authenticated_only
def disconnect():
    print str(current_user.id) + ' disconnected'


@socketio.on('send message', namespace='/chat')
@authenticated_only
def send_message(message):
    print 'recieved'
    msg = dict()
    msg['from'] = str(current_user.id)
    msg['to'] = message.get('to', '')
    msg['type'] = message.get('type', '')
    msg['data'] = message.get('data_1', '')
    data_2 = str(message.get('data_2'))
    if msg['type'] != 'text':
        f = open('messages/count.txt')
        count = int(f.readline())
        f.close()
        f = open('messages/media_'+str(count)+'.txt', 'w')
        f.write(msg['data'])
        msg['data'] = str(count)
        f.close()
        count += 1
        f = open('messages/media_'+str(count)+'.txt', 'w')
        f.write(message.get('data_2'))
        data_2 = str(count)
        f.close()
        count += 1
        f = open('messages/count.txt', 'w')
        f.write(str(count))
        f.close()
    f = open('messages/'+msg['to']+'_'+msg['from']+'.txt', 'a')
    f.write(str(msg['from'])+'\n'+str(msg['type'])+'\n'+str(str(msg['data']).encode('string_escape'))+'\n')
    f.close()
    f = open('messages/'+msg['from']+'_'+msg['to']+'.txt', 'a')
    f.write(str(msg['from'])+'\n'+str(msg['type'])+'\n'+str(data_2.encode('string_escape'))+'\n')
    f.close()
    if active_users.get(str(message.get('to', '')), False):
        emit('receive message', msg, room=str(msg['to']))
    else:
        emit('error', {'message': 'User Offline'})
