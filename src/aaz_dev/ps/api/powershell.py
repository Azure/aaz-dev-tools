from flask import Blueprint, jsonify, request, url_for

from utils.config import Config
from utils import exceptions
from ps.controller.ps_module_manager import PSModuleManager
from app.url_converters import PSNamesPathConverter
# from command.controller.specs_manager import AAZSpecsManager
import logging
import re

logging.basicConfig(level="INFO")


bp = Blueprint('powershell', __name__, url_prefix='/PS/Powershell')


@bp.route("/Path", methods=("GET", ))
def powershell_path():
    if Config.POWERSHELL_PATH is None:
        raise exceptions.InvalidAPIUsage("PowerShell path is not set, please add `--ps` option to `aaz-dev run` command or set up `AAZ_POWERSHELL_PATH` environment variable")
    return jsonify({"path": Config.POWERSHELL_PATH})


@bp.route("/Modules", methods=("GET", "POST"))
def powershell_modules():
    manager = PSModuleManager()
    if request.method == "GET":
        modules = manager.list_modules()
        result = []
        for module in modules:
            result.append({
                **module,
                'url': url_for('powershell.powershell_module', module_names=module['name']),
            })
        return jsonify(result)
    elif request.method == "POST":
        # create a new module in powershell
        data = request.get_json()
        if not data or not isinstance(data, dict) or 'name' not in data:
            raise exceptions.InvalidAPIUsage("Invalid request body")
        if not re.match(PSNamesPathConverter.regex, data['name'].split('/')):
            raise exceptions.InvalidAPIUsage("Invalid module name")
        module_names = data['name'].split('/')
        # make sure the name is follow the PSNamesPathConverter.regex
        module = manager.create_new_mod(module_names)
        result = module.to_primitive()
        result['url'] = url_for('powershell.powershell_module', module_names=module.name)
    else:
        raise NotImplementedError()
    return jsonify(result)


@bp.route("/Modules/<PSNamesPath:module_names>", methods=("GET",))
def powershell_module(module_names):
    manager = PSModuleManager()
    if request.method == "GET":
        module = manager.load_module(module_names)
        result = module.to_primitive()
        result['url'] = url_for('powershell.powershell_module', module_names=result['name'])
    else:
        raise NotImplementedError()
    return jsonify(result)


@bp.route("/Modules/<PSNamesPath:module_names>/Generate", methods=("POST", ))
def powershell_module_generate(module_names):
    manager = PSModuleManager()
    manager.generate_module(module_names)
    return jsonify({"message": "Module generated successfully"})
