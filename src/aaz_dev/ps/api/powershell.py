from flask import Blueprint, jsonify, request, url_for

from utils.config import Config
from utils import exceptions
from command.controller.specs_manager import AAZSpecsManager
import logging

logging.basicConfig(level="INFO")


bp = Blueprint('powershell', __name__, url_prefix='/PS/Powershell')


@bp.route("/Path", methods=("GET", "PUT"))
def powershell_path():
    if request.method == "GET":
        return jsonify({"path": Config.POWERSHELL_PATH})
    elif request.method == "PUT":
        data = request.json
        try:
            Config.validate_and_setup_powershell_path(None, None, data["path"])
        except ValueError as e:
            raise exceptions.InvalidAPIUsage(str(e))
        return jsonify({"path": Config.POWERSHELL_PATH})
