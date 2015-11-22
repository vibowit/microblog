import os
from flask import Flask
from flask.json import JSONEncoder
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask.ext.openid import OpenID
from flask.ext.mail import Mail
from flask.ext.babel import Babel, lazy_gettext
from .momentsjs import momentsjs

from config import basedir, ADMINS, MAIL_SERVER, MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD

app = Flask(__name__)
app.config.from_object('config')
app.jinja_env.globals['momentsjs'] = momentsjs

class CustomJSONEncoder(JSONEncoder):
    """This class adds support for lazy translation texts to Flask's
    JSON encoder. This is necessary when flashing translated texts."""
    def default(self, obj):
        from speaklater import is_lazy_string
        if is_lazy_string(obj):
            try:
                return unicode(obj)  # python 2
            except NameError:
                return str(obj)  # python 3
        return super(CustomJSONEncoder, self).default(obj)

app.json_encoder = CustomJSONEncoder

lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'
lm.login_message = lazy_gettext('Please log in to access this page.')

oid = OpenID(app, os.path.join(basedir, 'tmp'))
db = SQLAlchemy(app)
mail = Mail(app)
babel= Babel(app)

if not app.debug:
    import logging
    from logging.handlers import SMTPHandler
    credentials = None
    if MAIL_USERNAME or MAIL_PASSWORD:
        credentials = (MAIL_USERNAME, MAIL_PASSWORD)
    mail_handler = SMTPHandler((MAIL_SERVER, MAIL_PORT), 'no-reply@' + MAIL_SERVER, ADMINS, 'micro blog failure', credentials)
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)

from app import views, models

