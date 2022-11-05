from flask import Blueprint, Response, jsonify, request
from tinydb import TinyDB, Query
from time import time

temperature_api = Blueprint('temperature', __name__)
database = TinyDB('C:\\Users\\Dell\\PycharmProjects\\reefAquariumController\\database\\db.json', indent=4).table("temperature")


@temperature_api.route("/status", methods=["GET"])
def status():
    data = {'alarm': database.get(Query().type == 'alarm')['state'],
            'temperature': database.get(Query().type == 'temperature')['value']}
    return jsonify(data), 200


@temperature_api.route("/settings", methods=["GET", "POST"])
def settings():
    if request.method == "POST":
        database.update({'value': request.json['alarm_level']}, Query().type == 'alarm_level')
        return Response(status=200)
    elif request.method == "GET":
        data = {'alarm_level': database.get(Query().type == 'alarm_level')['value']}
        return jsonify(data), 200
    else:
        return Response(status=405)
