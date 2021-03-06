import os
import threading
from queue import Queue, Empty
from flask import Flask, g
from werkzeug.serving import is_running_from_reloader
from bmpi import wifiServer, views, logger


wifi_srv = wifiServer.wifiServer()

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

    with app.app_context():

        from .views.terminal import terminal_bp
        from .views.ui import ui_bp
        from .views.start import start_bp

        app.register_blueprint(terminal_bp)
        app.register_blueprint(ui_bp)
        app.register_blueprint(start_bp)

        #wifi_srv = wifiServer.wifiServer()
        app.wifi_srv = wifi_srv

        return app

