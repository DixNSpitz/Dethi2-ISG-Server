import os
import logging

from datetime import datetime
from logging.handlers import RotatingFileHandler

from flask import Flask
from flask_login import current_user

from isg_api.globals import db, login, migrate, bootstrap
from isg_api.models import SensorData, SensorType, SmartLeaf, Plant


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)

    # The server will have all the config set by now that has been in the .env-File during initialization-
    # All suceeding settings will be additional or overwriting those from the .env-File!
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_object('default_config')
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # Flask-Sqlalchemy props have to be loaded manually...
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['FLASK_SQLALCHEMY_DATABASE_URI']
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.environ['FLASK_SQLALCHEMY_TRACK_MODIFICATIONS']

    # Mail-Server-Config...
    if 'FLASK_SECRET_KEY' in os.environ:
        app.config['SECRET_KEY'] = os.environ['FLASK_SECRET_KEY']

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Bootstrap support
    bootstrap.init_app(app)

    # Database
    db.init_app(app)
    migrate.init_app(app, db)

    # Login-Manager
    login.init_app(app)

    # Blueprints
    from isg_api import main, errors, auth
    app.register_blueprint(auth.bp, url_prefix='/auth')
    app.register_blueprint(main.bp)
    app.register_blueprint(errors.bp)

    from isg_api.models import User

    @app.before_request
    def before_request():
        if current_user.is_authenticated:
            current_user.last_seen = datetime.utcnow()
            db.session.commit()

    @app.shell_context_processor
    def make_shell_context():
        return {'db': db, 'User': User, 'SensorData': SensorData, 'SensorType': SensorType, 'SmartLeaf': SmartLeaf, 'Plant': Plant}

    # Mail-Logging-Handler
    if not app.debug and not app.testing:
        # Rotational-File-Logging-Handler
        if not os.path.exists('logs'):
            os.mkdir('logs')

        file_handler = RotatingFileHandler('logs/isg-api.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('ISG-API startup')

    return app
