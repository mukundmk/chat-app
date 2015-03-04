__author__ = 'mukundmk'

import ssl
from app import app

SSL_CERTIFICATE = 'certificates/server.crt'
SSL_KEY = 'certificates/server2.key'
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
ssl_context.load_cert_chain(SSL_CERTIFICATE, SSL_KEY)
app.run(debug=True, ssl_context=ssl_context)