import time

from flask import Blueprint, Response, jsonify, request, redirect, render_template, url_for
from database.db import Database
from datetime import datetime


def notes_api(database: Database):
    notes = Blueprint('notes', __name__)

    @notes.route("/", methods=["GET", "DELETE"])
    def get():
        note_list = database.select(table='notes', single=False, append=' ORDER BY id DESC')
        answer = []
        for note in note_list:
            date_time = note[1].split(" ")
            date = date_time[0]
            time = date_time[1]
            answer.append({'id': note[0], 'date': date, 'time': time, 'content': note[2]})
        return render_template("html/notes/notes.html", note_list=answer)

    @notes.route("/add", methods=["POST"])
    def add():
        note = str(request.form.get('note'))
        date = datetime.now().strftime('%d-%m-%y %H:%M')
        database.insert(table='notes', columns=['date_time', 'note'], values=[date, note], force_que_execution=True)
        return redirect('/notes')

    @notes.route("/update", methods=["POST", "GET"])
    def update():
        if request.method == 'GET':
            element = database.select(table='notes', where=f'id={request.args.get("id")}', single=False)[0]
            note = {'id': element[0], 'date': element[1], 'content': element[2]}
            return render_template("html/notes/crud.html", note=note)
        if request.method == 'POST':
            new_content = str(request.form.get('content'))
            database.update(table='notes', column='note', value=new_content, where=f'id = {int(request.form.get("id"))}', force_que_execution=True)
            return redirect('/notes')

    @notes.route("/delete", methods=["POST"])
    def delete():
        database.delete(table='notes', where=f'id = {request.args.get("id")}', force_que_execution=True)
        return redirect('/notes')

    return notes
