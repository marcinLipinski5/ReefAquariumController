from flask import Blueprint, Response, jsonify, request, render_template, redirect
from tinydb import TinyDB, Query
from time import time
import logging

feeding_api = Blueprint('feeding_api', __name__)
database = TinyDB('C:\\Users\\Dell\\PycharmProjects\\reefAquariumController\\database\\db.json', indent=4).table("feeding")


@feeding_api.route("/start", methods=["POST"])
def start():
    command = request.get_json(force=True)['activate']
    if command and database.get(Query().type == 'is_feeding_time')['state']:
        return Response(status=304)
    is_feeding_time = False
    start_time = 0.0
    if command:
        is_feeding_time = True
        start_time = time()
        logging.info("Feeding started. Stopping all pumps.")
    else:
        logging.info("Feeding stopped. Starting all pumps.")
    database.update({'state': is_feeding_time}, Query().type == 'is_feeding_time')
    database.update({'timestamp': start_time}, Query().type == 'start_time')
    return Response(status=200)


@feeding_api.route("/status", methods=["GET"])
def status():
    data = {"is_feeding_time": database.get(Query().type == 'is_feeding_time')['state'],
            "feeding_duration": database.get(Query().type == 'feeding_duration')['seconds']}
    start_time = database.get(Query().type == 'start_time')['timestamp']
    if start_time != 0:
        calculated_time = round(database.get(Query().type == 'feeding_duration')['seconds'] - (time() - start_time))
        data['remaining_time'] = calculated_time
        if calculated_time < 0:
            database.update({'state': False}, Query().type == 'is_feeding_time')
            data['remaining_time'] = database.get(Query().type == 'feeding_duration')['seconds']
            logging.warning("Feeding system error!")
    else:
        data['remaining_time'] = database.get(Query().type == 'feeding_duration')['seconds']
    return jsonify(data), 200


@feeding_api.route("/settings", methods=["GET", "POST"])
def settings():
    if request.method == "POST":
        database.update({'seconds': int(request.form.get('feeding_time'))}, Query().type == 'feeding_duration')
        return redirect('/')
    elif request.method == "GET":
        data = {'feeding_duration': database.get(Query().type == 'feeding_duration')['seconds']}
        return jsonify(data), 200
    else:
        return Response(status=405)
