from flask import Flask, url_for, request, render_template
from api.feeding.api import feeding_api
from api.auto_refill.api import auto_refill_api
import logging

app = Flask(__name__)
app.register_blueprint(feeding_api, url_prefix='/feeding')
app.register_blueprint(auto_refill_api, url_prefix='/auto_refill')


@app.route('/', methods=["GET"])
def hello():
    return render_template("index.html")


class Server:

    @staticmethod
    def run():
        app.run()


if __name__ == "__main__":
    Server().run()
