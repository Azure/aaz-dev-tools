from flask import Blueprint, jsonify, request, url_for

from utils.config import Config
from utils import exceptions
from cli.controller.az_module_manager import AzModuleManager, AzMainManager, AzExtensionManager
from cli.model.atomic import CLIModule
from command.controller.specs_manager import AAZSpecsManager


bp = Blueprint('az', __name__, url_prefix='/CLI/Az')


@bp.route("/Profiles", methods=("GET", ))
def az_profiles():
    return jsonify(Config.CLI_PROFILES)


@bp.route("/AAZ/Specs/CommandTree/Nodes/<names_path:node_names>/Transfer", methods=("POST", ))
def az_utils_nodes(node_names):
    if node_names[0] != AAZSpecsManager.COMMAND_TREE_ROOT_NAME:
        raise exceptions.ResourceNotFind("Command group not exist")
    if len(node_names) < 2:
        raise exceptions.ResourceNotFind(f"CommandGroup '{' '.join(node_names)}' not find.")
    node_names = node_names[1:]
    manager = AzModuleManager()
    command_group = manager.build_command_group_from_aaz(*node_names)
    if command_group is None:
        raise exceptions.ResourceNotFind(f"CommandGroup '{' '.join(node_names)}' not find.")
    result = command_group.to_primitive()
    return jsonify(result)


@bp.route("/AAZ/Specs/CommandTree/Nodes/<names_path:node_names>/Leaves/<name:leaf_name>/Versions/<base64:version_name>/Transfer", methods=("POST", ))
def az_utils_leaves(node_names, leaf_name, version_name):
    if node_names[0] != AAZSpecsManager.COMMAND_TREE_ROOT_NAME:
        raise exceptions.ResourceNotFind("Command group not exist")
    node_names = node_names[1:]
    manager = AzModuleManager()
    command = manager.build_command_from_aaz(*node_names, leaf_name, version_name=version_name)
    if command is None:
        raise exceptions.ResourceNotFind(f"Command '{' '.join([*node_names, leaf_name])}' not find.")
    result = command.to_primitive()
    return jsonify(result)


@bp.route("/Main/Modules", methods=("GET", "POST"))
def az_main_modules():
    manager = AzMainManager()
    if request.method == "POST":
        data = request.get_json()
        if not data or not isinstance(data, dict) or 'name' not in data:
            raise exceptions.InvalidAPIUsage("Invalid request body")
        mod_name = data['name']
        module = manager.create_new_mod(mod_name)
        result = module.to_primitive()
        result['url'] = url_for('az.az_main_module', module_name=module.name)
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


@bp.route("/Main/Modules/<Name:module_name>", methods=("GET", "PUT"))
def az_main_module(module_name):
    manager = AzMainManager()
    if request.method == "PUT":
        data = request.get_json()
        if 'profiles' not in data:
            raise exceptions.InvalidAPIUsage("miss profiles for module")
        module = CLIModule({
            "name": module_name,
            "profiles": data['profiles']
        })
        module = manager.update_module(module_name, module.profiles)
        result = module.to_primitive()
        result['url'] = url_for('az.az_main_module', module_name=module.name)
    elif request.method == "GET":
        module = manager.load_module(module_name)
        result = module.to_primitive()
        result['url'] = url_for('az.az_main_module', module_name=module.name)
    else:
        raise NotImplementedError()
    return jsonify(result)


@bp.route("/Extension/Modules", methods=("GET", "POST"))
def az_extension_modules():
    manager = AzExtensionManager()
    if request.method == "POST":
        data = request.get_json()
        if not data or not isinstance(data, dict) or 'name' not in data:
            raise exceptions.InvalidAPIUsage("Invalid request body")
        mod_name = data['name']
        module = manager.create_new_mod(mod_name)
        result = module.to_primitive()
        result['url'] = url_for('az.az_extension_module', module_name=module.name)
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


@bp.route("/Extension/Modules/<Name:module_name>", methods=("GET", "PUT"))
def az_extension_module(module_name):
    manager = AzExtensionManager()
    if request.method == "PUT":
        data = request.get_json()
        if 'profiles' not in data:
            raise exceptions.InvalidAPIUsage("miss profiles for module")
        module = CLIModule({
            "name": module_name,
            "profiles": data['profiles']
        })
        module = manager.update_module(module_name, module.profiles)
        result = module.to_primitive()
        result['url'] = url_for('az.az_extension_module', module_name=module.name)
    elif request.method == "GET":
        module = manager.load_module(module_name)
        result = module.to_primitive()
        result['url'] = url_for('az.az_extension_module', module_name=module.name)
    else:
        raise NotImplementedError()
    return jsonify(result)
