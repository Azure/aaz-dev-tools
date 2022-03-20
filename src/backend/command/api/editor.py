import os

from flask import Blueprint, jsonify, request, url_for

from command.controller.workspace_manager import WorkspaceManager
from utils import exceptions

bp = Blueprint('editor', __name__, url_prefix='/AAZ/Editor')


@bp.route("/Workspaces", methods=("GET", "POST"))
def editor_workspaces():
    if request.method == "POST":
        # create a new workspace
        # the name of workspace is required
        data = request.get_json()
        if not data or not isinstance(data, dict) or 'name' not in data or 'plane' not in data:
            raise exceptions.InvalidAPIUsage("Invalid request body")
        name = data['name']
        plane = data['plane']
        manager = WorkspaceManager.new(name, plane)
        manager.save()
        result = manager.ws.to_primitive()
        result.update({
            'url': url_for('editor.editor_workspace', name=manager.name),
            'folder': manager.folder,
            'updated': os.path.getmtime(manager.path)
        })
    elif request.method == "GET":
        result = []
        for ws in WorkspaceManager.list_workspaces():
            result.append({
                **ws,
                'url': url_for('editor.editor_workspace', name=ws['name']),
            })
    else:
        raise NotImplementedError(request.method)

    return jsonify(result)


@bp.route("/Workspaces/<name>", methods=("GET", "DELETE"))
def editor_workspace(name):
    manager = WorkspaceManager(name)
    if request.method == "GET":
        manager.load()
    elif request.method == "DELETE":
        if manager.delete():
            return '', 200
        else:
            return '', 204  # resource not found
    else:
        raise NotImplementedError()

    result = manager.ws.to_primitive()
    result.update({
        'url': url_for('editor.editor_workspace', name=manager.name),
        'folder': manager.folder,
        'updated': os.path.getmtime(manager.path)
    })
    return jsonify(result)


@bp.route("/Workspaces/<name>/Generate", methods=("POST",))
def editor_workspace_generate(name):
    manager = WorkspaceManager(name)
    manager.load()
    manager.generate_to_aaz()
    return "", 200


# command tree operations
@bp.route("/Workspaces/<name>/CommandTree/Nodes/<names_path:node_names>", methods=("GET", "POST", "PATCH", "DELETE"))
def editor_workspace_command_tree_node(name, node_names):
    if node_names[0] != WorkspaceManager.COMMAND_TREE_ROOT_NAME:
        raise exceptions.ResourceNotFind("Command group not exist")
    node_names = node_names[1:]

    manager = WorkspaceManager(name)
    manager.load()
    node = manager.find_command_tree_node(*node_names)
    if not node and request.method != "DELETE":
        raise exceptions.ResourceNotFind("Command group not exist")

    if request.method == "GET":
        # get current node
        result = node.to_primitive()
    elif request.method == "POST":
        # create sub node
        data = request.get_json()
        if 'name' not in data or not data['name']:
            raise exceptions.InvalidAPIUsage("Invalid request")
        sub_node_names = data['name'].split(' ')
        node = manager.create_command_tree_nodes(*node_names, *sub_node_names)
        manager.save()
        result = node.to_primitive()
    elif request.method == "PATCH":
        # update help or stage of node
        data = request.get_json()
        if 'help' in data:
            node = manager.update_command_tree_node_help(*node_names, help=data['help'])
        if 'stage' in data and node.stage != data['stage']:
            node = manager.update_command_tree_node_stage(*node_names, stage=data['stage'])
        manager.save()
        result = node.to_primitive()
    elif request.method == "DELETE":
        # delete node
        if len(node_names) < 1:
            raise exceptions.InvalidAPIUsage("Not support to delete command tree root")
        if not manager.delete_command_tree_node(*node_names):
            return '', 204  # resource not found
        manager.save()
        return '', 200
    else:
        raise NotImplementedError()
    return jsonify(result)


@bp.route("/Workspaces/<name>/CommandTree/Nodes/<names_path:node_names>/Rename", methods=("POST",))
def editor_workspace_command_tree_node_rename(name, node_names):
    if node_names[0] != WorkspaceManager.COMMAND_TREE_ROOT_NAME:
        raise exceptions.ResourceNotFind("Command group not exist")
    node_names = node_names[1:]
    if not node_names:
        raise exceptions.InvalidAPIUsage("Cannot Rename root node")

    manager = WorkspaceManager(name)
    manager.load()
    if not manager.find_command_tree_node(*node_names):
        raise exceptions.ResourceNotFind("Command group not exist")

    data = request.get_json()
    new_name = data.get("name", None)
    if not new_name or not isinstance(new_name, str):
        raise exceptions.InvalidAPIUsage("Invalid request")

    new_node_names = new_name.split(' ')
    node = manager.rename_command_tree_node(*node_names, new_node_names=new_node_names)
    result = node.to_primitive()
    manager.save()
    return jsonify(result)


@bp.route("/Workspaces/<name>/CommandTree/Nodes/<names_path:node_names>/Leaves/<name:leaf_name>",
          methods=("GET", "PATCH"))
def editor_workspace_command(name, node_names, leaf_name):
    if node_names[0] != WorkspaceManager.COMMAND_TREE_ROOT_NAME:
        raise exceptions.ResourceNotFind("Command not exist")
    node_names = node_names[1:]

    manager = WorkspaceManager(name)
    manager.load()
    leaf = manager.find_command_tree_leaf(*node_names, leaf_name)
    if not leaf:
        raise exceptions.ResourceNotFind("Command not exist")

    if request.method == "GET":
        # get the command configuration
        cfg_editor = manager.load_cfg_editor_by_command(leaf)
        command = cfg_editor.find_command(*leaf.names)
        result = command.to_primitive()
    elif request.method == "PATCH":
        # update help or stage of node
        data = request.get_json()
        if 'help' in data:
            leaf = manager.update_command_tree_leaf_help(*leaf.names, help=data['help'])
        if 'stage' in data and leaf.stage != data['stage']:
            leaf = manager.update_command_tree_leaf_stage(*leaf.names, stage=data['stage'])
        if 'examples' in data:
            leaf = manager.update_command_tree_leaf_examples(*leaf.names, examples=data['examples'])
        cfg_editor = manager.load_cfg_editor_by_command(leaf)
        command = cfg_editor.find_command(*leaf.names)
        result = command.to_primitive()
        manager.save()
    else:
        raise NotImplementedError()

    del result['name']
    result.update({
        'names': leaf.names,
        'help': leaf.help.to_primitive(),
        'stage': leaf.stage,
    })
    if leaf.examples:
        result['examples'] = [e.to_primitive() for e in leaf.examples]

    return jsonify(result)


@bp.route("/Workspaces/<name>/CommandTree/Nodes/<names_path:node_names>/Leaves/<name:leaf_name>/Rename",
          methods=("POST",))
def editor_workspace_command_rename(name, node_names, leaf_name):
    if node_names[0] != WorkspaceManager.COMMAND_TREE_ROOT_NAME:
        raise exceptions.ResourceNotFind("Command not exist")
    node_names = node_names[1:]

    manager = WorkspaceManager(name)
    manager.load()
    if not manager.find_command_tree_leaf(*node_names, leaf_name):
        raise exceptions.ResourceNotFind("Command not exist")

    data = request.get_json()
    new_name = data.get("name", None)
    if not new_name or not isinstance(new_name, str):
        raise exceptions.InvalidAPIUsage("Invalid request")

    new_leaf_names = new_name.split(' ')
    new_leaf = manager.rename_command_tree_leaf(*node_names, leaf_name, new_leaf_names=new_leaf_names)
    cfg_editor = manager.load_cfg_editor_by_command(new_leaf)
    command = cfg_editor.find_command(*new_leaf.names)

    result = command.to_primitive()
    del result['name']
    result.update({
        'names': new_leaf.names,
        'help': new_leaf.help.to_primitive(),
        'stage': new_leaf.stage
    })
    if new_leaf.examples:
        result['examples'] = [e.to_primitive() for e in new_leaf.examples]

    manager.save()
    return jsonify(result)


# command tree resource operations
@bp.route("/Workspaces/<name>/CommandTree/Nodes/<names_path:node_names>/AddSwagger", methods=("POST",))
def editor_workspace_tree_node_resources(name, node_names):
    if node_names[0] != WorkspaceManager.COMMAND_TREE_ROOT_NAME:
        raise exceptions.ResourceNotFind("Command group not exist")
    node_names = node_names[1:]

    manager = WorkspaceManager(name)
    manager.load()
    if not manager.find_command_tree_node(*node_names):
        raise exceptions.ResourceNotFind("Command group not exist")

    # add new resource
    data = request.get_json()
    if not isinstance(data, dict):
        raise exceptions.InvalidAPIUsage("Invalid request")

    try:
        mod_names = data['module']
        version = data['version']
        resources = data['resources']
    except KeyError:
        raise exceptions.InvalidAPIUsage("Invalid request")

    manager.add_new_resources_by_swagger(
        mod_names=mod_names,
        version=version,
        resources=resources,
        *node_names
    )
    manager.save()
    return "", 200


@bp.route("/Workspaces/<name>/CommandTree/Nodes/<names_path:node_names>/Resources", methods=("GET",))
def editor_workspace_resources(name, node_names):
    if node_names[0] != WorkspaceManager.COMMAND_TREE_ROOT_NAME:
        raise exceptions.ResourceNotFind("Command group not exist")
    node_names = node_names[1:]

    manager = WorkspaceManager(name)
    manager.load()
    if not manager.find_command_tree_node(*node_names):
        raise exceptions.ResourceNotFind("Command group not exist")

    resources = manager.get_resources(*node_names)

    result = [r.to_primitive() for r in resources]
    return jsonify(result)


@bp.route("/Workspaces/<name>/Resources/Merge", methods=("POST",))
def editor_workspace_resources_merge(name):
    manager = WorkspaceManager(name)
    manager.load()
    data = request.get_json()
    if "mainResource" not in data or "plusResource" not in data:
        raise exceptions.InvalidAPIUsage("Invalid request")
    main_resource_id = data["mainResource"]["id"]
    main_resource_version = data["mainResource"]["version"]
    plus_resource_id = data["plusResource"]["id"]
    plus_resource_version = data["plusResource"]["version"]
    if not manager.merge_resources(main_resource_id, main_resource_version, plus_resource_id, plus_resource_version):
        raise exceptions.ResourceConflict("Cannot merge resources")
    manager.save()
    return "", 200


@bp.route("/Workspaces/<name>/Resources/<base64:resource_id>/V/<base64:version>", methods=("DELETE",))
def editor_workspace_resource(name, resource_id, version):
    manager = WorkspaceManager(name)
    manager.load()
    if not manager.remove_resource(resource_id, version):
        return "", 204
    manager.save()
    return "", 200


@bp.route("/Workspaces/<name>/Resources/<base64:resource_id>/V/<base64:version>/Commands", methods=("GET",))
def list_workspace_resource_related_commands(name, resource_id, version):
    manager = WorkspaceManager(name)
    manager.load()
    commands = manager.list_commands_by_resource(resource_id, version)
    result = [command.to_primitive() for command in commands]
    return jsonify(result)


@bp.route("/Workspaces/<name>/CommandTree/Nodes/<names_path:node_names>/Resources/ReloadSwagger", methods=("POST",))
def editor_workspace_resource_reload_swagger(name, node_names):
    # update resource by reloading swagger
    data = request.get_json()
    # data = (resource_id, swagger_version)
    # TODO:
    raise NotImplementedError()


@bp.route("/Workspaces/<name>/CommandTree/Nodes/<names_path:node_names>/Try", methods=("POST",))
def editor_workspace_try_command_group(name, node_names):
    if node_names[0] != WorkspaceManager.COMMAND_TREE_ROOT_NAME:
        raise exceptions.ResourceNotFind("Command group not exist")
    node_names = node_names[1:]

    manager = WorkspaceManager(name)
    manager.load()
    if not manager.find_command_tree_node(*node_names):
        raise exceptions.ResourceNotFind("Command group not exist")

    # try sub commands by installed as a try extension of cli
    raise NotImplementedError()


@bp.route("/Workspaces/<name>/CommandTree/Nodes/<names_path:node_names>/Leaves/<name:leaf_name>/Try", methods=("POST",))
def editor_workspace_try_command(name, node_names, leaf_name):
    if node_names[0] != WorkspaceManager.COMMAND_TREE_ROOT_NAME:
        raise exceptions.ResourceNotFind("Command not exist")
    node_names = node_names[1:]

    manager = WorkspaceManager(name)
    manager.load()
    if not manager.find_command_tree_leaf(*node_names, leaf_name):
        raise exceptions.ResourceNotFind("Command not exist")

    # try command by installed as a try extension of cli
    raise NotImplementedError()
