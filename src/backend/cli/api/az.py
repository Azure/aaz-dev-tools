from flask import Blueprint, jsonify, request, url_for

from utils.config import Config
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
        # TODO: create new module in main repo
        raise NotImplementedError()
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
        # TODO: create new module in extension repo
        raise NotImplementedError()
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
