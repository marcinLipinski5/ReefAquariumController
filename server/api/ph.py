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
            database.update(table='ph', column='alarm_level', value=int(request.form.get('alarm_level')))
            return redirect('/')
        elif request.method == "GET":
            data = {'alarm_level': database.select(table='ph', column='alarm_level')}
            return jsonify(data), 200
        else:
            return Response(status=405)

    @ph.route("/plot")
    def plot_historic_data():
        historic_data = database.select(table='ph_history', column='date_time, ph', single=False)
        df = pd.DataFrame(historic_data, columns=['date', 'pH'])
        fig = px.line(df, x='date', y='pH', title='pH')
        graph_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return render_template('historic_plot.html', graphJSON=graph_json)

    return ph
