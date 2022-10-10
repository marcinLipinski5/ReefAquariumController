from flask import Flask, url_for, request, render_template
from api.feeding.api import feeding_api

app = Flask(__name__)
app.register_blueprint(feeding_api, url_prefix='/feeding')


@app.route('/', methods=["GET"])
def hello():
    return render_template("index.html")


if __name__ == "__main__":
    app.run()
