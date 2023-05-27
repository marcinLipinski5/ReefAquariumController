from flask import Blueprint, Response, jsonify, request, render_template, redirect
from database.db import Database
from time import time
import logging


def feeding_api(database: Database):
    feeding = Blueprint('feeding_api', __name__)

    @feeding.route("/start", methods=["POST"])
    def start():
        command = request.get_json(force=True)['activate']
        if command and database.select(table='feeding', column='is_feeding_time'):
            return Response(status=304)
        is_feeding_time = False
        if command:
            is_feeding_time = True
            logging.info("Feeding started. Stopping all pumps.")
        else:
            logging.info("Feeding stopped. Starting all pumps.")
        database.update(table='feeding', column='is_feeding_time', value=is_feeding_time)
        return Response(status=200)

    @feeding.route("/status", methods=["GET"])
    def status():
        data = {"is_feeding_time": database.select(table='feeding', column='is_feeding_time', boolean_needed=True),
                "feeding_duration": database.select(table='feeding', column='feeding_duration')}
        start_time = database.select(table='feeding', column='start_time')
        if start_time != 0:
            calculated_time = round(database.select(table='feeding', column='feeding_duration') - (time() - start_time))
            data['remaining_time'] = calculated_time
            if calculated_time < 0:  # calculation error and state reset
                database.update(table='feeding', column='is_feeding_time', value=False, boolean_needed=True)
                database.update(table='feeding', column='start_time', value=0.0)
                data['remaining_time'] = database.select(table='feeding', column='feeding_duration')
                logging.warning("Feeding system error!")
        else:
            data['remaining_time'] = database.select(table='feeding', column='feeding_duration')
        return jsonify(data), 200

    @feeding.route("/settings", methods=["GET", "POST"])
    def settings():
        if request.method == "POST":
            database.update(table='feeding', column='feeding_duration', value=int(request.form.get('feeding_time')))
            database.update(table='light', column="enable_feeding_light", value=bool(request.form.get('feeding_light')), boolean_needed=True)
            return redirect('/')
        elif request.method == "GET":
            data = {'feeding_duration': database.select(table='feeding', column='feeding_duration'),
                    'enable_feeding_light': database.select(table='light', column='enable_feeding_light', boolean_needed=True)}
            return jsonify(data), 200
        else:
            return Response(status=405)

    return feeding
