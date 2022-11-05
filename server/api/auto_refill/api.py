from flask import Blueprint, Response, jsonify, request
from tinydb import TinyDB, Query
from time import time

auto_refill_api = Blueprint('auto_refill_api', __name__)
database = TinyDB('C:\\Users\\Dell\\PycharmProjects\\reefAquariumController\\database\\db.json', indent=4).table("auto_refill")


@auto_refill_api.route("/status", methods=["GET"])
def status():
    data = {'alarm': database.get(Query().type == 'alarm')['status'],
            'daily_refill_flow': database.get(Query().type == 'daily_refill_flow')['flow']}
    return jsonify(data), 200


@auto_refill_api.route("/settings", methods=["GET", "POST"])
def settings():
    if request.method == "POST":
        database.update({'flow': request.json['max_daily_refill_flow']}, Query().type == 'max_daily_refill_flow')
        database.update({'time': request.json['refill_max_time_in_seconds']}, Query().type == 'refill_max_time_in_seconds')
        return Response(status=200)
    elif request.method == "GET":
        data = {'max_daily_refill_flow': database.get(Query().type == 'max_daily_refill_flow')['flow'],
                'refill_max_time_in_seconds': database.get(Query().type == 'refill_max_time_in_seconds')['time']}
        return jsonify(data), 200
    else:
        return Response(status=405)
