import flask
from flask import Flask, url_for, request


app = Flask(__name__)


@app.route('/', methods=["GET"])
def hello():
    return flask.render_template("index.html")

@app.route('/dupa', methods=["POST"])
def dupa():
    aaa = request.form["refill_pump_max_working_time"]
    print(aaa)
    return aaa


if __name__ == "__main__":
    app.run()
