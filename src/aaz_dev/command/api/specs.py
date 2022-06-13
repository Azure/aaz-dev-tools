from flask import Blueprint, jsonify, request, url_for
from utils import exceptions
from command.controller.specs_manager import AAZSpecsManager


bp = Blueprint('specs', __name__, url_prefix='/AAZ/Specs')


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
