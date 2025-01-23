import os

from flask import Blueprint, jsonify, request, url_for, redirect
from utils import exceptions
from utils.config import Config
from cli.model.view import CLIViewProfile
from ps.controller.ps_sketch_profile_builder import PSSketchProfileBuilder


bp = Blueprint('ps_editor', __name__, url_prefix='/PS/Editor')

@bp.route("/GenerateSketcheProfile", methods=("POST", ))
def generate_sketch_profile():
    if request.method == "POST":
        data = request.get_json()
        if not data or 'cliProfile' not in data:
            raise exceptions.InvalidAPIUsage("Invalid request body")
        cli_profile = CLIViewProfile(raw_data=data['cliProfile'])
        cli_profile.validate()
        builder = PSSketchProfileBuilder()
        profile = builder(cli_profile)
        return jsonify(profile.to_native())
    else:
        raise NotImplementedError(request.method)
