import time

from flask import Blueprint, Response, jsonify, request, redirect, render_template
from database.db import Database
from datetime import datetime


def notes_api(database: Database):
    notes = Blueprint('notes', __name__)

    @notes.route("/", methods=["GET"])
    def get():
        note_list = database.select(table='notes', single=False)
        answer = []
        for note in note_list:
            answer.append({'id': note[0], 'date': note[1], 'content': note[2]})
        return render_template("notes.html", note_list=answer)

    @notes.route("/add", methods=["POST"])
    def add():
        note = str(request.form.get('note'))
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        database.insert(table='notes', columns=['date_time', 'note'], values=[date, note])
        time.sleep(0.5)
        return redirect('/notes')


    return notes
