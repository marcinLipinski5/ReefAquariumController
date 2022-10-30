from flask import Blueprint, Response, jsonify, request
from tinydb import TinyDB, Query
from time import time
import logging

feeding_api = Blueprint('feeding_api', __name__)
database = TinyDB('C:\\Users\\Dell\\PycharmProjects\\reefAquariumController\\database\\db.json', indent=4).table("feeding")


@feeding_api.route("/start", methods=["POST"])
def start():
    logging.info("Feeding started. Stopping all pumps.")
    database.update({'status': True}, Query().type == 'is_feeding_time')
    database.update({'timestamp': time()}, Query().type == 'time_started')
    return Response(status=200)


@feeding_api.route("/status", methods=["GET"])
def status():
    data = {}
    is_feeding_time = database.get(Query().type == 'is_feeding_time')['status']
    data["is_feeding_time"] = is_feeding_time
    time_started = database.get(Query().type == 'start_time')['timestamp']
    if time_started != 0:
        calculated_time = round(database.get(Query().type == 'feeding_duration')['seconds'] - (time() - time_started))
        data['remaining_time'] = calculated_time
        if calculated_time < 0:
            logging.warning("Feeding system error!")
    else:
        data['remaining_time'] = database.get(Query().type == 'feeding_duration')['seconds']
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
