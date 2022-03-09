from flask import Blueprint, jsonify, request, url_for

from utils.config import Config
from utils import exceptions
from cli.controller.az_main_manager import AzMainManager
from cli.controller.az_extension_manager import AzExtensionManager


bp = Blueprint('az', __name__, url_prefix='/CLI/Az')


@bp.route("/Profiles", methods=("GET", ))
def az_profiles():
    return jsonify(Config.CLI_PROFILES)


@bp.route("/Main/Modules", methods=("GET", "POST"))
def az_main_modules():
    manager = AzMainManager()
    if request.method == "POST":
        data = request.get_json()
        if not data or not isinstance(data, dict) or 'name' not in data:
            raise exceptions.InvalidAPIUsage("Invalid request body")
        mod_name = data['name']
        module = manager.create_new_mod(mod_name)
        result = {
            **module,
            'url': url_for('az.az_main_module', module_name=module['name']),
        }
    elif request.method == "GET":
        # list available modules
        modules = manager.list_modules()
        result = []
        for module in modules:
            result.append({
                **module,
                'url': url_for('az.az_main_module', module_name=module['name']),
            })
    else:
        raise NotImplementedError()

    return jsonify(result)


@bp.route("/Main/Modules/<Name:module_name>", methods=("GET", ))
def az_main_module(module_name):
    manager = AzMainManager()
    manager.load_module(module_name)
    # TODO:
    return "", 200


@bp.route("/Extension/Modules", methods=("GET", "POST"))
def az_extension_modules():
    manager = AzExtensionManager()
    if request.method == "POST":
        data = request.get_json()
        if not data or not isinstance(data, dict) or 'name' not in data:
            raise exceptions.InvalidAPIUsage("Invalid request body")
        mod_name = data['name']
        module = manager.create_new_mod(mod_name)
        result = {
            **module,
            'url': url_for('az.az_extension_module', module_name=module['name']),
        }
    elif request.method == "GET":
        # list available modules
        modules = manager.list_modules()
        result = []
        for module in modules:
            result.append({
                **module,
                'url': url_for('az.az_extension_module', module_name=module['name']),
            })
    else:
        raise NotImplementedError()

    return jsonify(result)


@bp.route("/Extension/Modules/<Name:module_name>", methods=("GET", "POST"))
def az_extension_module(module_name):
    manager = AzExtensionManager()
    manager.load_module(module_name)
    # TODO:
    return "", 200
