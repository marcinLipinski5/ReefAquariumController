import time

from flask import Blueprint, Response, jsonify, request, redirect, render_template, url_for
from database.db import Database
from datetime import datetime


def water_quality_api(database: Database):
    water_quality = Blueprint('water_quality', __name__)

    @water_quality.route("/", methods=["GET", "DELETE"])
    def get():
        column_list = database.get_columns(table='water_quality')
        measurement_list = database.select(table='water_quality', single=False, append=' ORDER BY id DESC')
        date = datetime.now().strftime('%d-%m-%y %H:%M')
        answer = []
        for measure in measurement_list:
            dictionary = {}
            for index, value in enumerate(measure):
                dictionary[column_list[index]] = value
            answer.append(dictionary)
        return render_template("html/water_quality/water_quality.html", column_list=column_list, measurement_list=answer, date=date)

    # @notes.route("/add", methods=["POST"])
    # def add():
    #     note = str(request.form.get('note'))
    #     date = datetime.now().strftime('%d-%m-%y %H:%M')
    #     database.insert(table='notes', columns=['date_time', 'note'], values=[date, note], force_que_execution=True)
    #     return redirect('/notes')
    #
    # @notes.route("/update", methods=["POST", "GET"])
    # def update():
    #     if request.method == 'GET':
    #         element = database.select(table='notes', where=f'id={request.args.get("id")}', single=False)[0]
    #         note = {'id': element[0], 'date': element[1], 'content': element[2]}
    #         return render_template("html/notes/crud.html", note=note)
    #     if request.method == 'POST':
    #         new_content = str(request.form.get('content'))
    #         database.update(table='notes', column='note', value=new_content, where=f'id = {int(request.form.get("id"))}', force_que_execution=True)
    #         return redirect('/notes')
    #
    # @notes.route("/delete", methods=["POST"])
    # def delete():
    #     database.delete(table='notes', where=f'id = {request.args.get("id")}', force_que_execution=True)
    #     return redirect('/notes')

    return water_quality
