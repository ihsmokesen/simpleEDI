import flask as flask
from flask import Flask
from threading import Thread
import os


class ShutdownGetRequestHandler(Thread):
    PASSWORD = "1234"
    app_core = None
    flask_app = Flask(__name__)

    def __init__(self, app_core):
        super().__init__()

        @self.flask_app.route("/shutdown")
        def get_shutdown_password():
            password = flask.request.args.get('password')
            if password == self.PASSWORD:
                self.app_core.finish_all()
                os.kill(os.getpid(), 9)
                return None
            return "Password is not valid"

        self.app_core = app_core

    def run(self):
        try:
            self.flask_app.run(port=5001)
        except Exception as exc:
            print(exc)
