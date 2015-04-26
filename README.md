# chat-app

## Requirements
- python 2.7.9
- mysql
- neo4j
- flask
- flask-sqlalchemy
- flask-socketio
- flask-login
- flask-mail
- gevent
- py2neo
- pycrypto
##### Optional
- nginx
    
## Instructions
- Edit config.py in app. 
    * Set username and password for mysql db.
    * Set neo4j url
    * Set app secret key and salt for token.
    * Set username and password for gmail smtp.
- Create db chat-app in mysql.
- Start neo4j.
- To run:
    * python run.py
- Optionally you can use nginx to reverse proxy for ssl
    
