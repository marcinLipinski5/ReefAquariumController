from flask import Flask, render_template
from flask_cors import CORS
from flask_socketio import SocketIO

from api.auto_refill.api import auto_refill_api
from api.fan.api import fan_api
from api.feeding.api import feeding_api
from api.temperature.api import temperature_api

app = Flask(__name__, static_url_path='',
            static_folder='static',
            template_folder='static')
app.url_map.strict_slashes = False
socketio = SocketIO(app)
thread = None

CORS(app)
app.register_blueprint(feeding_api, url_prefix='/feeding', template_folder="templates")
app.register_blueprint(auto_refill_api, url_prefix='/auto_refill')
app.register_blueprint(temperature_api, url_prefix="/temperature")
app.register_blueprint(fan_api, url_prefix='/fan')


@app.route('/', methods=["GET"])
def hello():
    return render_template("index.html")


class Server:

    @staticmethod
    def run():
        app.run()


if __name__ == "__main__":
    Server().run()
