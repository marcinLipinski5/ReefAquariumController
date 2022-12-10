from flask import Blueprint, Response, jsonify, request, redirect, g
from tinydb import TinyDB, Query
from database.db import Database


def temperature_api(database: Database):
    temperature = Blueprint('temperature', __name__)
    # database = TinyDB('C:\\Users\\Dell\\PycharmProjects\\reefAquariumController\\database\\db.json', indent=4).table("temperature")

    @temperature.route("/status", methods=["GET"])
    def status():
        data = {'alarm': database.select(table='temperature', column='alarm', boolean_needed=True),
                'temperature': database.select(table='temperature', column='temperature')}

        print(database.select(table='temperature', column='temperature'))
        return jsonify(data), 200

    @temperature.route("/settings", methods=["GET", "POST"])
    def settings():
        if request.method == "POST":
            database.update(table='temperature', column='alarm_level', value=int(request.form.get('alarm_level')))
            return redirect('/')
        elif request.method == "GET":
            data = {'alarm_level': database.select(table='temperature', column='alarm_level')}
            return jsonify(data), 200
        else:
            return Response(status=405)

    return temperature
