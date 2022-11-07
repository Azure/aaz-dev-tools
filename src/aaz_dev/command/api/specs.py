from flask import Blueprint, jsonify, request, url_for
from utils import exceptions
from command.controller.specs_manager import AAZSpecsManager
from cli.controller.portal_cli_generator import PortalCliGenerator
import json


bp = Blueprint('specs', __name__, url_prefix='/AAZ/Specs')

@bp.route("/Portal/Generate", methods=("GET",))
def portal_generate():
    manager = AAZSpecsManager()
    root = manager.find_command_group()
    if not root:
        raise exceptions.ResourceNotFind("Command group not exist")
    cmd_nodes_list = manager.get_command_tree()
    portal_cli_generator = PortalCliGenerator()
    cmd_portal_list = []
    for node_path in cmd_nodes_list:
        # node_path = ['aaz', 'change-analysis', 'list']
        node_names = node_path[1:-1]
        leaf_name = node_path[-1]
        leaf = manager.find_command(*node_names, leaf_name)
        if not leaf or not leaf.versions:
            raise exceptions.ResourceNotFind("Command group: " + " ".join(leaf.names) + " not exist")
        if not leaf.versions:
            raise exceptions.ResourceNotFind("Command group: " + " ".join(leaf.names) + " version not exist")
        target_version = leaf.versions[0]
        if not target_version:
            raise exceptions.ResourceNotFind("Command: " + " ".join(leaf.names) + " version not exist")

        cfg_reader = manager.load_resource_cfg_reader_by_command_with_version(leaf, version=target_version)
        cmd_cfg = cfg_reader.find_command(*leaf.names)
        cmd_portal_info = portal_cli_generator.generate_command_portal_raw(cmd_cfg, leaf, target_version)
        if cmd_portal_info:
            cmd_portal_list.append(cmd_portal_info)

    portal_cli_generator.generate_cmds_portal(cmd_portal_list)
    result = root.to_primitive()
    return jsonify(result)

@bp.route("/Portal/<names_path:node_names>/Generate/Leaves/<name:leaf_name>/version/<target_version>", methods=("GET",))
def portal_cmd_generate(node_names, leaf_name, target_version):
    if node_names[0] != AAZSpecsManager.COMMAND_TREE_ROOT_NAME:
        raise exceptions.ResourceNotFind("Command group not exist")
    #node_names = ['aaz', 'change-analysis', 'list']
    node_names = node_names[1:]

    manager = AAZSpecsManager()
    leaf = manager.find_command(*node_names, leaf_name)
    if not leaf:
        raise exceptions.ResourceNotFind("Command group not exist")

    #target_version = "2021-04-01"
    version = None
    for v in (leaf.versions or []):
        if v.name == target_version:
            version = v
            break

    if not version:
        raise exceptions.ResourceNotFind("Command of version not exist")
    portal_cli_generator = PortalCliGenerator()
    cfg_reader = manager.load_resource_cfg_reader_by_command_with_version(leaf, version=version)
    cmd_cfg = cfg_reader.find_command(*leaf.names)
    cmd_portal_info = portal_cli_generator.generator_command_portal(cmd_cfg, leaf, version)
    file_path = "-".join(leaf.names) + ".json"
    with open(file_path, "w") as f_out:
        f_out.write(json.dumps(cmd_portal_info, indent=4))

    result = cmd_cfg.to_primitive()
    del result['name']
    result.update({
        'names': leaf.names,
        'help': leaf.help.to_primitive(),
        'stage': version.stage,
    })
    if version.examples:
        result['examples'] = version.examples[0].to_primitive()

    return jsonify(result)

# modules
@bp.route("/CommandTree/Nodes/<names_path:node_names>", methods=("GET",))
def command_tree_node(node_names):
    if node_names[0] != AAZSpecsManager.COMMAND_TREE_ROOT_NAME:
        raise exceptions.ResourceNotFind("Command group not exist")
    node_names = node_names[1:]

    manager = AAZSpecsManager()
    node = manager.find_command_group(*node_names)
    if not node:
        raise exceptions.ResourceNotFind("Command group not exist")

    result = node.to_primitive()
    return jsonify(result)


@bp.route("/CommandTree/Nodes/<names_path:node_names>/Leaves/<name:leaf_name>", methods=("GET",))
def command_tree_leaf(node_names, leaf_name):
    if node_names[0] != AAZSpecsManager.COMMAND_TREE_ROOT_NAME:
        raise exceptions.ResourceNotFind("Command not exist")
    node_names = node_names[1:]

    manager = AAZSpecsManager()
    leaf = manager.find_command(*node_names, leaf_name)
    if not leaf:
        raise exceptions.ResourceNotFind("Command not exist")

    result = leaf.to_primitive()
    return jsonify(result)


@bp.route("/CommandTree/Nodes/<names_path:node_names>/Leaves/<name:leaf_name>/Versions/<base64:version_name>", methods=("GET",))
def aaz_command_in_version(node_names, leaf_name, version_name):
    if node_names[0] != AAZSpecsManager.COMMAND_TREE_ROOT_NAME:
        raise exceptions.ResourceNotFind("Command not exist")
    node_names = node_names[1:]

    manager = AAZSpecsManager()
    leaf = manager.find_command(*node_names, leaf_name)
    if not leaf:
        raise exceptions.ResourceNotFind("Command not exist")

    version = None
    for v in (leaf.versions or []):
        if v.name == version_name:
            version = v
            break

    if not version:
        raise exceptions.ResourceNotFind("Command of version not exist")

    cfg_reader = manager.load_resource_cfg_reader_by_command_with_version(leaf, version=version)
    cmd_cfg = cfg_reader.find_command(*leaf.names)

    result = cmd_cfg.to_primitive()
    del result['name']
    result.update({
        'names': leaf.names,
        'help': leaf.help.to_primitive(),
        'stage': version.stage,
    })
    if version.examples:
        result['examples'] = version.examples.to_primitive()

    return jsonify(result)


@bp.route("/Resources/<plane>/<base64:resource_id>", methods=("GET", ))
def get_resource(plane, resource_id):
    manager = AAZSpecsManager()
    versions = manager.get_resource_versions(plane, resource_id)
    if versions is None:
        raise exceptions.ResourceNotFind("Resource not exist")
    result = {
        "id": resource_id,
        "versions": versions
    }
    return jsonify(result)


@bp.route("/Resources/<plane>/Filter", methods=("Post", ))
def filter_resources(plane):
    data = request.get_json()
    if 'resources' not in data:
        raise exceptions.InvalidAPIUsage("Invalid request body")
    manager = AAZSpecsManager()

    result = {
        'resources': []
    }
    for resource_id in data['resources']:
        versions = manager.get_resource_versions(plane, resource_id)
        if versions is None:
            continue
        result['resources'].append({
            "id": resource_id,
            "versions": versions,
        })

    return jsonify(result)
