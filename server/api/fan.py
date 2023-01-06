from flask import Blueprint, Response, jsonify, request, redirect
from database.db import Database


def fan_api(database: Database):
    fan = Blueprint('fan', __name__)

    @fan.route("/status", methods=["GET"])
    def status():
        current_level = database.select(table='fan', column='current_level')
        duty_cycle = database.select(table='fan', column=f'{current_level}_level_duty_cycle')
        data = {'level': current_level.replace('_level_duty_cycle', ''),
                'duty_cycle': duty_cycle}
        return jsonify(data), 200

    @fan.route("/settings", methods=["GET", "POST"])
    def settings():
        levels = ['freeze', 'normal', 'alarm']
        if request.method == "POST":
            for level in levels:
                database.update(table='fan', column=f'{level}_level_duty_cycle', value=int(request.form.get(f'{level}_level')))
                database.update(table='fan', column='update_needed', value=True, boolean_needed=True)
            return redirect('/')
        elif request.method == "GET":
            data = {}
            for level in levels:
                data[f'{level}_level_duty_cycle'] = database.select(table='fan', column=f'{level}_level_duty_cycle')
            return jsonify(data), 200
        else:
            return Response(status=405)

    return fan
