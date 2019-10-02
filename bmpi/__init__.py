import os
import threading
from flask import Flask, g
from werkzeug.serving import is_running_from_reloader
from bmpi import wifiServer, logger



def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_object('config')
    app.config.from_pyfile('config.py')

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from .views.index import index_bp
    from .views.terminal import terminal_bp
    from .views.test import test_bp

    app.register_blueprint(index_bp)
    app.register_blueprint(terminal_bp)
    app.register_blueprint(test_bp)

    wifi_srv = wifiServer.wifiServer(logger)


    return app