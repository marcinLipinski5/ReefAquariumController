from flask import Blueprint, Response, jsonify, request, redirect
from tinydb import TinyDB, Query

fan_api = Blueprint('fan', __name__)
database = TinyDB('C:\\Users\\Dell\\PycharmProjects\\reefAquariumController\\database\\db.json', indent=4).table("fan")


@fan_api.route("/status", methods=["GET"])
def status():
    current_level = database.get(Query().type == 'current_level')['level']
    duty_cycle = database.get(Query().type == f'{current_level}_level_duty_cycle')['value']
    data = {'level': current_level.replace('_level_duty_cycle', ''),
            'duty_cycle': duty_cycle}
    return jsonify(data), 200


@fan_api.route("/settings", methods=["GET", "POST"])
def settings():
    levels = ['freeze', 'normal', 'alarm']
    if request.method == "POST":
        for level in levels:
            database.update({'value': int(request.form.get(f'{level}_level'))}, Query().type == f'{level}_level_duty_cycle')
        return redirect('/')
    elif request.method == "GET":
        data = {}
        for level in levels:
            data[f'{level}_level_duty_cycle'] = database.get(Query().type == f'{level}_level_duty_cycle')['value']
        return jsonify(data), 200
    else:
        return Response(status=405)
