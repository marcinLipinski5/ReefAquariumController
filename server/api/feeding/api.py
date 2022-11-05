from flask import Blueprint, Response, jsonify, request
from tinydb import TinyDB, Query
from time import time
import logging

feeding_api = Blueprint('feeding_api', __name__)
database = TinyDB('C:\\Users\\Dell\\PycharmProjects\\reefAquariumController\\database\\db.json', indent=4).table("feeding")


@feeding_api.route("/start", methods=["POST"])
def start():
    command = request.get_json(force=True)['activate']
    is_feeding_time = False
    start_time = 0.0
    if command:
        is_feeding_time = True
        start_time = time()
        logging.info("Feeding started. Stopping all pumps.")
    else:
        logging.info("Feeding stopped. Starting all pumps.")
    database.update({'status': is_feeding_time}, Query().type == 'is_feeding_time')
    database.update({'timestamp': start_time}, Query().type == 'start_time')
    return Response(status=200)


@feeding_api.route("/feeding-duration", methods=["GET"])
def feeding_duration():
    data = {'feeding_duration': database.get(Query().type == 'feeding_duration')['seconds']}
    return jsonify(data), 200


@feeding_api.route("/settings", methods=["GET", "POST"])
def settings():
    if request.method == "POST":
        database.update({'seconds': request.json['feeding_duration']}, Query().type == 'feeding_duration')
        return Response(status=200)
    elif request.method == "GET":
        data = {'feeding_duration': database.get(Query().type == 'feeding_duration')['seconds']}
        return jsonify(data), 200
    else:
        return Response(status=405)
