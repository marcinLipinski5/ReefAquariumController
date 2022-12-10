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
        self.database = database

    def get_database(self):
        return self.database

    app = Flask(__name__, static_url_path='',
                static_folder='static',
                template_folder='static')

    @staticmethod
    @app.route('/', methods=["GET"])
    def index():
        return render_template("index.html")

    def run(self):
        logging.info('Server started!')
        self.app.url_map.strict_slashes = False
        CORS(self.app)
        self.app.register_blueprint(feeding_api, url_prefix='/feeding', template_folder="templates")
        self.app.register_blueprint(auto_refill_api, url_prefix='/auto_refill')
        self.app.register_blueprint(temperature_api(self.get_database()), url_prefix="/temperature")
        self.app.register_blueprint(fan_api, url_prefix='/fan')
        self.app.run()


if __name__ == "__main__":
    Server().run()
