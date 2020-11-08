import logging
import os
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler

from flask import Flask
from flask_awscognito import AWSCognitoAuthentication
from flask_bootstrap import Bootstrap
from flask_cognito import CognitoAuth
from flask_dynamo import Dynamo
from flask_login import LoginManager

from app.flask_edits import Edits
from config import Config

login = LoginManager()
login.login_view = 'auth.login'
bootstrap = Bootstrap()
dynamo = Dynamo()
aws_auth = AWSCognitoAuthentication()
cogauth = CognitoAuth()
edits = Edits()


def create_app(config_class=Config):
    application = Flask(__name__)

    application.config.from_object(config_class)

    login.init_app(application)
    bootstrap.init_app(application)
    dynamo.init_app(application)
    aws_auth.init_app(application)
    cogauth.init_app(application)
    edits.init_app(application)

    from app.errors import bp as errors_bp
    application.register_blueprint(errors_bp)

    with application.app_context():
        from app.auth import bp as auth_bp
        application.register_blueprint(auth_bp, url_prefix='/auth')

    with application.app_context():
        from app.main import bp as main_bp
        application.register_blueprint(main_bp)

    @application.template_filter('datetimeformat')
    def datetimeformat(value):
        return datetime.fromtimestamp(value, tz=timezone.utc).strftime('%d/%m/%Y %-I:%M%p')

    @application.template_filter('datetimeHMformat')
    def datetimeHMformat(value):
        dt = datetime.fromtimestamp(value, tz=timezone.utc)
        dts = dt.strftime('%Y-%m-%d %H:%M')
        return dts

    if not application.debug and not application.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/officaldanc.log',
                                           maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        application.logger.addHandler(file_handler)

        application.logger.setLevel(logging.INFO)
        application.logger.info('Microblog startup')

    return application
