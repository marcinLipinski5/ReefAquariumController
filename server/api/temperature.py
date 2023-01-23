from flask import Blueprint, Response, jsonify, request, redirect, render_template
from database.db import Database
import pandas as pd
import json
import plotly
import plotly.express as px


def temperature_api(database: Database):
    temperature = Blueprint('temperature', __name__)

    @temperature.route("/status", methods=["GET"])
    def status():
        data = {'alarm': database.select(table='temperature', column='alarm', boolean_needed=True),
                'temperature': database.select(table='temperature', column='temperature')}
        return jsonify(data), 200

    @temperature.route("/settings", methods=["GET", "POST"])
    def settings():
        if request.method == "POST":
            database.update(table='temperature', column='alarm_level', value=int(request.form.get('alarm_level')))
            database.update(table='temperature', column='update_needed', value=True, boolean_needed=True)
            return redirect('/')
        elif request.method == "GET":
            data = {'alarm_level': database.select(table='temperature', column='alarm_level')}
            return jsonify(data), 200
        else:
            return Response(status=405)

    @temperature.route("/plot")
    def plot_historic_data():
        historic_data = database.select(table='temperature_history', column='date_time, temperature', single=False)
        df = pd.DataFrame(historic_data, columns=['date', 'temperature [*C]'])
        fig = px.line(df, x='date', y='temperature [*C]', title='Temperature')
        graph_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return render_template('html/plot.html', graphJSON=graph_json)

    return temperature
