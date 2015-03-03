__author__ = 'mukundmk'

from flask import *
import os
from flask.ext.sqlalchemy import *
from flask.ext.socketio import *

app = Flask(__name__)
app.config.from_pyfile('config.py', silent=True)
socketio = SocketIO(app)

@app.route('/post_message', methods=['POST'])
def post_message():
    f = open('messages.txt', 'a')
    f.write(request.form['name']+':'+request.form['msg']+'\n')
    f.close()
    return 'Success'


def read_file(name):
    f = open('messages.txt')
    for l in f:
        from_name, msg = l.strip().split(':')
        if from_name == name:
            from_name = 'Me'
        print 'data: %s\n' % (from_name+':'+msg)
        yield 'data: %s\n' % (from_name+':'+msg)

@app.route('/get_messages')
def get_messages():
    name = request.args['name']
    return Response(read_file(name), mimetype='text/event-stream')

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.debug = True
    socketio.run(app, port=5001)