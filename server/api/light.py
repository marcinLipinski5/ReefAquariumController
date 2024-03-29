from flask import Blueprint, Response, jsonify, request, redirect
from database.db import Database


def light_api(database: Database):
    light = Blueprint('light', __name__)

    @light.route("/settings", methods=["GET", "POST"])
    def settings():
        if request.method == "POST":
            database.update(table='light', column='start_time', value=str(request.form.get('start_time')))
            database.update(table='light', column='stop_time', value=str(request.form.get('stop_time')))
            database.update(table='light', column='power', value=str(request.form.get('power')))
            database.update(table='light', column='update_needed', value=True, boolean_needed=True)
            return redirect('/')
        elif request.method == "GET":
            data = {'start_time': database.select(table='light', column='start_time'),
                    'stop_time': database.select(table='light', column='stop_time'),
                    'power': database.select(table='light', column='power')}
            return jsonify(data), 200
        else:
            return Response(status=405)

    return light
