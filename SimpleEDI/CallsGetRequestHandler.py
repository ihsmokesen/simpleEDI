from flask import Flask
from threading import Thread


class CallsGetRequestHandler(Thread):
    database_manager = None
    flask_app = Flask(__name__)

    def __init__(self, database_manager):
        super().__init__()

        @self.flask_app.route("/calls/<number>")
        def get_calls(number):
            return self.database_manager.get_calls_dict_by_number(number)

        self.database_manager = database_manager

    def run(self):
        try:
            self.flask_app.run()
        except Exception as exc:
            print(exc)
