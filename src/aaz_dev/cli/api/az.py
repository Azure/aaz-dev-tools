from flask import Blueprint, jsonify, request, url_for

from utils.config import Config
from utils import exceptions
from cli.controller.az_module_manager import AzMainManager, AzExtensionManager
from cli.controller.portal_cli_generator import PortalCliGenerator
from cli.model.view import CLIModule
from command.controller.specs_manager import AAZSpecsManager


bp = Blueprint('az', __name__, url_prefix='/CLI/Az')


@bp.route("/Profiles", methods=("GET", ))
def az_profiles():
    return jsonify(Config.CLI_PROFILES)


@bp.route("/Main/Modules", methods=("GET", "POST"))
def az_main_modules():
    manager = AzMainManager()
    if request.method == "POST":
        # create a new module in azure-cli
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
        # create a new extension in azure-cli-extensions
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

@bp.route("/Main/Modules/<Name:module_name>/ExportPortalConfig", methods=("POST",))
def portal_generate_main_module(module_name):
    az_main_manager = AzMainManager()
    if az_main_manager.has_module(module_name):
        cli_module = az_main_manager.load_module(module_name)
        print("Input module: {0} in cli".format(module_name))
    else:
        print("Invalid input module: {0}, please check".format(module_name))
        return

    aaz_spec_manager = AAZSpecsManager()
    root = aaz_spec_manager.find_command_group()
    if not root:
        raise exceptions.ResourceNotFind("Command group not exist")
    cmd_nodes_list = aaz_spec_manager.get_module_command_tree(module_name)
    portal_cli_generator = PortalCliGenerator()
    cmd_portal_list = []
    for node_path in cmd_nodes_list:
        # node_path = ['aaz', 'change-analysis', 'list']
        cmd_module = node_path[1]
        if cmd_module != module_name:
            continue
        node_names = node_path[1:-1]
        leaf_name = node_path[-1]
        leaf = aaz_spec_manager.find_command(*node_names, leaf_name)
        if not leaf or not leaf.versions:
            print("Command group: " + " ".join(leaf.names) + " not exist")
            continue
        if not leaf.versions:
            print("Command group: " + " ".join(leaf.names) + " version not exist")
            continue
        registered_version = az_main_manager.find_cmd_registered_version(cli_module['profiles']['latest'], *node_path[1:])
        if not registered_version:
            print("Cannot find {0} registered version".format(" ".join(node_path[1:])))
            continue
        target_version = None
        for v in (leaf.versions or []):
            if v.name == registered_version:
                target_version = v
                break
        if not target_version:
            print("Command: " + " ".join(leaf.names) + " registered version " + registered_version + " not exist")
            continue

        cfg_reader = aaz_spec_manager.load_resource_cfg_reader_by_command_with_version(leaf, version=target_version)
        cmd_cfg = cfg_reader.find_command(*leaf.names)
        cmd_portal_info = portal_cli_generator.generate_command_portal_raw(cmd_cfg, leaf, target_version)
        if cmd_portal_info:
            cmd_portal_list.append(cmd_portal_info)

    portal_cli_generator.generate_cmds_portal(cmd_portal_list)
    return "done"

@bp.route("/Extension/Modules/<Name:module_name>/ExportPortalConfig", methods=("POST",))
def portal_generate_extension_module(module_name):
    az_ext_manager = AzExtensionManager()
    if az_ext_manager.has_module(module_name):
        cli_module = az_ext_manager.load_module(module_name)
        print("Input module: {0} in cli extension".format(module_name))
    else:
        print("Invalid input module: {0}, please check".format(module_name))
        return

    aaz_spec_manager = AAZSpecsManager()
    root = aaz_spec_manager.find_command_group()
    if not root:
        raise exceptions.ResourceNotFind("Command group not exist")
    cmd_nodes_list = aaz_spec_manager.get_module_command_tree(module_name)
    portal_cli_generator = PortalCliGenerator()
    cmd_portal_list = []
    for node_path in cmd_nodes_list:
        # node_path = ['aaz', 'change-analysis', 'list']
        cmd_module = node_path[1]
        if cmd_module != module_name:
            continue
        node_names = node_path[1:-1]
        leaf_name = node_path[-1]
        leaf = aaz_spec_manager.find_command(*node_names, leaf_name)
        if not leaf or not leaf.versions:
            print("Command group: " + " ".join(leaf.names) + " not exist")
            continue
        if not leaf.versions:
            print("Command group: " + " ".join(leaf.names) + " version not exist")
            continue
        registered_version = az_ext_manager.find_cmd_registered_version(cli_module['profiles']['latest'], *node_path[1:])
        if not registered_version:
            print("Cannot find {0} registered version".format(" ".join(node_path[1:])))
            continue
        target_version = None
        for v in (leaf.versions or []):
            if v.name == registered_version:
                target_version = v
                break
        if not target_version:
            print("Command: " + " ".join(leaf.names) + " registered version " + registered_version + " not exist")
            continue

        cfg_reader = aaz_spec_manager.load_resource_cfg_reader_by_command_with_version(leaf, version=target_version)
        cmd_cfg = cfg_reader.find_command(*leaf.names)
        cmd_portal_info = portal_cli_generator.generate_command_portal_raw(cmd_cfg, leaf, target_version)
        if cmd_portal_info:
            cmd_portal_list.append(cmd_portal_info)

    portal_cli_generator.generate_cmds_portal(cmd_portal_list)
    return "done"
