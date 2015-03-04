__author__ = 'mukundmk'

import ssl
import sys
from app import app

SSL_CERTIFICATE = ''
SSL_KEY = ''

if len(sys.argv) > 1 and sys.argv[1] == 'ssl':
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    ssl_context.load_cert_chain(SSL_CERTIFICATE, SSL_KEY)
    app.run(debug=True, ssl_context=ssl_context)

else:
    app.run(debug=True)