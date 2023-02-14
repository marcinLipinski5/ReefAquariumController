import time

from flask import Blueprint, Response, jsonify, request, redirect, render_template
from database.db import Database
import pandas as pd
import json
import plotly
import plotly.express as px


def ph_api(database: Database):
    ph = Blueprint('ph', __name__)

    @ph.route("/status", methods=["GET"])
    def status():
        data = {'alarm': database.select(table='ph', column='alarm', boolean_needed=True),
                'ph': database.select(table='ph', column='ph')}
        return jsonify(data), 200

    @ph.route("/settings", methods=["GET", "POST"])
    def settings():
        if request.method == "POST":
            database.update(table='ph', column='alarm_level_up', value=float(request.form.get('alarm_level_up')))
            database.update(table='ph', column='alarm_level_down', value=float(request.form.get('alarm_level_down')))
            return redirect('/')
        elif request.method == "GET":
            data = {'alarm_level_up': database.select(table='ph', column='alarm_level_up'),
                    'alarm_level_down': database.select(table='ph', column='alarm_level_down'),
                    'process': database.select(table='ph', column='process'),
                    'm_factor': database.select(table='ph', column='m'),
                    'b_factor': database.select(table='ph', column='b'),
                    'last_voltage': database.select(table='ph', column='last_voltage')}
            return jsonify(data), 200
        else:
            return Response(status=405)

    @ph.route("/plot")
    def plot_historic_data():
        historic_data = database.select(table='ph_history', column='date_time, ph', single=False)
        df = pd.DataFrame(historic_data, columns=['date', 'pH'])
        fig = px.line(df, x='date', y='pH', title='pH')
        graph_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return render_template('html/plot.html', graphJSON=graph_json)

    @ph.route("/calibration", methods=["POST"])
    def calibration_start():
        database.update(table='ph', column='process', value="calibration")
        database.update(table='ph', column='calibration_time_start', value=time.time())
        database.update(table='ph', column='calibration_ph', value=str(request.form.get('ph')).replace(".", "_"))
        return '', 204

    @ph.route("/calibration/manual", methods=["POST"])
    def calibration_manual():
        database.update(table='ph', column='process', value='manual_calibration')
        database.update(table='ph', column='m', value=float(request.form.get('m_factor')))
        database.update(table='ph', column='b', value=float(request.form.get('b_factor')), force_que_execution=True)
        return redirect('/')

    return ph
