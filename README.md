# chat-app

## Requirements
- python 2.7.9
- flask
- flask-sqlalchemy
- flask-socketio
- flask-login
- flask-mail
- gevent
    
## Instructions
- Edit config.py in app. 
    * Set username and password for mysql db.
    * Set app secret key and salt for token.
    * Set username and password for gmail smtp.
- Create db chat-app in mysql.
- If using ssl configure in run.py
- To run:
    * with ssl    : python run.py ssl
    * without ssl : python run.py
