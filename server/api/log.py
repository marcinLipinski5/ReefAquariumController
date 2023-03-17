import os
from pathlib import Path

from flask import Blueprint, send_from_directory, render_template


def log_api(root_path: str):
    log = Blueprint('log', __name__)

    @log.route("/", methods=["GET"])
    def get():
        log_file = os.path.join(root_path, "aquarium_log.log")
        with open(log_file, 'r', encoding="UTF-8") as file_process:
            file_content = file_process.read().split("|")
        return render_template("html/log/log.html", log_list=file_content)
        # return send_from_directory(root_path, "aquarium_log.log", as_attachment=False)

    return log
