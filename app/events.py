__author__ = 'mukundmk'

from flask.ext.socketio import join_room, leave_room, emit
from flask.ext.login import current_user

from app import socketio, active_users


@socketio.on('connect', namespace='/chat')
def connect():
    join_room(str(current_user.id))
    msg = dict()
    msg['message'] = 'User connected'
    msg['userid'] = str(current_user.id)
    print str(current_user.id) +' connected'
    emit('connect', msg)


@socketio.on('disconnect', namespace='/chat')
def connect():
    print str(current_user.id) +' disconnected'


@socketio.on('send message', namespace='/chat')
def send_message(message):
    print 'msg received'
    msg = dict()
    msg['from'] = message.get('from', '')
    msg['to'] = message.get('to', '')
    msg['data'] = message.get('data', '')
    f = open('messages/'+msg['to']+'_'+msg['from']+'.txt', 'a')
    f.write(str(msg['from'])+'\n'+str(str(msg['data']).encode('string_escape'))+'\n')
    f.close()
    f = open('messages/'+msg['from']+'_'+msg['to']+'.txt', 'a')
    f.write(str(msg['from'])+'\n'+str(str(msg['data']).encode('string_escape'))+'\n')
    f.close()
    if active_users.get(str(message.get('to', '')), False):
        emit('receive message', msg, room=str(msg['to']))
    else:
        emit('error', {'message': 'User Offline'})
