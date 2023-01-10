import logging

from flask import Flask, render_template
from flask_cors import CORS
from database.db import Database

from server.api.auto_refill import auto_refill_api
from server.api.fan import fan_api
from server.api.feeding import feeding_api
from server.api.temperature import temperature_api
from server.api.ph import ph_api
from server.api.notes import notes_api


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
        self.app.register_blueprint(ph_api(self.__database), url_prefix="/ph")
        self.app.register_blueprint(notes_api(self.__database), url_prefix="/notes")
        logging.info('Server started!')

    def run(self):
        self.prepare()
        self.app.run(port=5001)

    def get_test_instance(self):
        self.prepare()
        self.app.testing = True
        return self.app.test_client()


if __name__ == "__main__":
    Server(Database()).run()
