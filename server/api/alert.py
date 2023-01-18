import time

from flask import Blueprint, Response, jsonify, request, redirect, render_template, url_for
from database.db import Database
from datetime import datetime


def alert_api(database: Database):
    alert = Blueprint('alert', __name__)

    @alert.route("/status", methods=["GET"])
    def get():
        alert_list = database.select(table='alert', single=False, where='status=1')
        answer = {}
        for alert in alert_list:
            answer[alert[1]] = {'id': alert[0], 'type': alert[1], 'date': alert[2], 'description': alert[3], 'action_endpoint': alert[5], 'button_text': alert[6]}
        return jsonify(answer), 200

    @alert.route("/clear", methods=["GET"])
    def clear():
        database.update(table='alert',
                        column='status',
                        value=False,
                        boolean_needed=True,
                        where=f'type="{request.args.get("type")}"',
                        force_que_execution=True)
        return redirect('/')

    return alert
