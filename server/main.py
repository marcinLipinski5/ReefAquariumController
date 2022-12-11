import logging

from flask import Flask, render_template, g
from flask_cors import CORS
from flask_socketio import SocketIO
from database.db import Database

from api.auto_refill.api import auto_refill_api
from api.fan.api import fan_api
from api.feeding.api import feeding_api
from api.temperature.api import temperature_api


class Server:

    def __init__(self, database: Database):
        self.__database = database

    app = Flask(__name__, static_url_path='',
                static_folder='static',
                template_folder='static')

    @staticmethod
    @app.route('/', methods=["GET"])
    def index():
        return render_template("index.html")

    def prepare(self):
        self.app.url_map.strict_slashes = False
        CORS(self.app)
        self.app.register_blueprint(feeding_api(self.__database), url_prefix='/feeding', template_folder="templates")
        self.app.register_blueprint(auto_refill_api(self.__database), url_prefix='/auto_refill')
        self.app.register_blueprint(temperature_api(self.__database), url_prefix="/temperature")
        self.app.register_blueprint(fan_api(self.__database), url_prefix='/fan')
        logging.info('Server started!')

    def run(self):
        self.prepare()
        self.app.run()

    def get_test_instance(self):
        self.prepare()
        return self.app.test_client()


if __name__ == "__main__":
    Server().run()
