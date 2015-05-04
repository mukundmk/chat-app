__author__ = 'mukundmk'

import ssl
import sys
from app import app, socketio

app.debug = True
socketio.run(app, host='0.0.0.0')