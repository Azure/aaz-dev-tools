from flask import Blueprint, jsonify, request, url_for

from utils.config import Config
from utils import exceptions
from command.controller.specs_manager import AAZSpecsManager
import logging

logging.basicConfig(level="INFO")


bp = Blueprint('autorest', __name__, url_prefix='/PS/Autorest')


@bp.route("/Directives", methods=("GET", ))
def az_profiles():
    return jsonify({"test": "test"})
