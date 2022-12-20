from flask import Blueprint, Response, jsonify, request, redirect, url_for

from database.db import Database


def auto_refill_api(database: Database):
    auto_refill = Blueprint('auto_refill_api', __name__)

    @auto_refill.route("/status", methods=["GET"])
    def status():
        data = {'alarm': database.select(table='auto_refill', column='alarm', boolean_needed=True),
                'daily_refill_flow': database.select(table='auto_refill', column='daily_refill_flow')}
        return jsonify(data), 200

    @auto_refill.route("/settings", methods=["GET", "POST"])
    def settings():
        if request.method == "POST":
            database.update(table='auto_refill', column='max_daily_refill_flow', value=int(request.form.get('max_daily_refill_flow')))
            database.update(table='auto_refill', column='refill_max_time_in_seconds', value=int(request.form.get('refill_max_time_in_seconds')))
            return redirect('/')
        elif request.method == "GET":
            data = {'max_daily_refill_flow': database.select(table='auto_refill', column='max_daily_refill_flow'),
                    'refill_max_time_in_seconds': database.select(table='auto_refill', column='refill_max_time_in_seconds'),
                    'calibration_flow': database.select(table='auto_refill', column='calibration_flow')}
            return jsonify(data), 200
        else:
            return Response(status=405)

    @auto_refill.route("/calibration/start", methods=["GET"])
    def calibration_start():
        database.update(table='auto_refill', column='calibration_stage', value="data_collecting")
        database.update(table='auto_refill', column='calibration', value=True, boolean_needed=True)
        return ('', 204)

    @auto_refill.route("/calibration/save", methods=["POST"])
    def calibration_save():
        if request.method == "POST":
            database.update(table='auto_refill', column='calibration', value=True, boolean_needed=True)
            database.update(table='auto_refill', column='calibration_stage', value="processing")
            database.update(table='auto_refill', column='calibration_flow', value=float(request.form.get('calibration_flow')))
            return redirect('/')
        else:
            return Response(status=405)

    return auto_refill
