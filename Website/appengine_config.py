import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))

from gaesessions import SessionMiddleware


def webapp_add_wsgi_middleware(app):
#    app = SessionMiddleware(app, cookie_key="omgzth1sstr1ngiss0r4nd0m")
    app = SessionMiddleware(app, cookie_key=os.urandom(64))
    return app
