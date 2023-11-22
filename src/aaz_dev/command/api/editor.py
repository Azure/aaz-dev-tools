import os

from flask import Blueprint, jsonify, request, url_for, redirect

from command.controller.workspace_manager import WorkspaceManager
from utils import exceptions
from utils.config import Config
from command.model.configuration._utils import CMDArgBuildPrefix

bp = Blueprint('editor', __name__, url_prefix='/AAZ/Editor')


@bp.route("/Workspaces", methods=("GET", "POST"))
def editor_workspaces():
    if request.method == "POST":
        # create a new workspace
        # the name of workspace is required
        data = request.get_json()
        if not data or not isinstance(data, dict) or 'name' not in data or 'plane' not in data or 'modNames' not in data or 'resourceProvider' not in data:
            raise exceptions.InvalidAPIUsage("Invalid request body")
        name = data['name']
        plane = data['plane']
        mod_names = data['modNames']
        resource_provider = data['resourceProvider']
        manager = WorkspaceManager.new(name, plane, mod_names, resource_provider)
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


@bp.route("/Workspaces/<name>/SwaggerDefault", methods=("GET",))
def get_workspace_swagger_default_options(name):
    manager = WorkspaceManager(name)
    manager.load()
    result = {
        "plane": manager.ws.plane,
        "modNames": manager.ws.mod_names if manager.ws.mod_names else Config.DEFAULT_SWAGGER_MODULE,
        "rpName": manager.ws.resource_provider if manager.ws.resource_provider else Config.DEFAULT_RESOURCE_PROVIDER,
    }
    if result["modNames"]:
        result["modNames"] = result["modNames"].split('/')
    return jsonify(result)


@bp.route("/Workspaces/<name>/Rename", methods=("POST",))
def rename_workspace(name):
    manager = WorkspaceManager(name)
    if request.method == "POST":
        data = request.get_json()
        if 'name' not in data or not data['name']:
            raise exceptions.InvalidAPIUsage("Invalid request")
        new_name = data['name'].strip()
        manager.rename(new_name)
        result = manager.ws.to_primitive()
        result.update({
            'url': url_for('editor.editor_workspace', name=manager.name),
            'folder': manager.folder,
            'updated': os.path.getmtime(manager.path)
        })
    else:
        raise NotImplementedError()
    return jsonify(result)


@bp.route("/Workspaces/<name>/Generate", methods=("POST",))
def editor_workspace_generate(name):
    manager = WorkspaceManager(name)
    manager.load()
    manager.generate_to_aaz()
    return "", 200


# client configuration
@bp.route("/Workspaces/<name>/ClientConfig", methods=("GET", "POST"))
def editor_workspace_client_config(name):
    manager = WorkspaceManager(name)
    manager.load()
    if request.method == "GET":
        cfg_editor = manager.load_client_cfg_editor()
        if not cfg_editor:
            raise exceptions.ResourceNotFind("Client configuration not exist")
    elif request.method == "POST":
        data = request.get_json()
        if 'auth' not in data:
            raise exceptions.InvalidAPIUsage("Invalid request: auth info is required.")
        if 'templates' not in data and 'resource' not in data:
            raise exceptions.InvalidAPIUsage("Invalid request: templates or resource is required for endpoints.")
        if 'resource' in data:
            if 'id' not in data['resource'] or 'version' not in data['resource'] or 'module' not in data['resource'] or 'subresource' not in data['resource']:
                raise exceptions.InvalidAPIUsage("Invalid request")
        cfg_editor = manager.create_cfg_editor(
            auth=data['auth'],
            templates=data.get('templates', None),
            arm_resource=data.get('resource', None),
        )
        manager.save()
    else:
        raise NotImplementedError()
    result = cfg_editor.cfg.to_primitive()
    return jsonify(result)

@bp.route("/Workspaces/<name>/ClientConfig/AAZ/Compare", methods=("POST",))
def compare_workspace_client_config_version_with_aaz(name):
    manager = WorkspaceManager(name)
    manager.load()
    if not manager.compare_client_cfg_with_spec():
        raise exceptions.ResourceConflict("Client configuration is out of data in current workspace. Please reload it from aaz repo.")
    return "", 200


@bp.route("/Workspaces/<name>/ClientConfig/AAZ/Inherit", methods=("POST",))
def inherit_workspace_client_config_from_aaz(name):
    manager = WorkspaceManager(name)
    manager.load()
    manager.inherit_client_cfg_from_spec()
    manager.save()
    cfg_editor = manager.load_client_cfg_editor()
    if not cfg_editor:
        raise exceptions.ResourceNotFind("Client configuration not exist")
    result = cfg_editor.cfg.to_primitive()
    return jsonify(result)


@bp.route("/Workspaces/<name>/ClientConfig/Arguments/<arg_var>", methods=("GET", "PATCH"))
def editor_workspace_client_config_argument(name, arg_var):
    manager = WorkspaceManager(name)
    manager.load()
    cfg_editor = manager.load_client_cfg_editor()
    if not cfg_editor:
        raise exceptions.ResourceNotFind("Client configuration not exist")
    arg = cfg_editor.find_arg_by_var(arg_var=arg_var)
    if not arg:
        raise exceptions.ResourceNotFind("Argument not exist")

    if request.method == "GET":
        result = arg.to_primitive()
    elif request.method == "PATCH":
        data = request.get_json()
        cfg_editor.update_arg_by_var(arg_var=arg_var, **data)
        manager.save()
        arg = cfg_editor.find_arg_by_var(arg_var=arg_var)
        result = arg.to_primitive()
    else:
        raise NotImplementedError()
    return jsonify(result)


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
        if 'confirmation' in data:
            cfg_editor.update_command_confirmation(*leaf.names, confirmation=data['confirmation'])
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

    # add client configuration argument group in the command response
    client_cfg = manager.load_client_cfg_editor()
    if client_cfg and client_cfg.cfg.arg_group:
        arg_groups = result.get('argGroups', [])
        result['argGroups'] = [*arg_groups, client_cfg.cfg.arg_group.to_primitive()]

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


@bp.route("/Workspaces/<name>/CommandTree/Nodes/<names_path:node_names>/Leaves/<name:leaf_name>/Arguments/<arg_var>",
          methods=("GET", "PATCH"))
def editor_workspace_command_argument(name, node_names, leaf_name, arg_var):
    if arg_var.startswith(CMDArgBuildPrefix.ClientEndpoint):
        # redirect to client config argument
        return redirect(url_for('editor.editor_workspace_client_config_argument', name=name, arg_var=arg_var))

    if node_names[0] != WorkspaceManager.COMMAND_TREE_ROOT_NAME:
        raise exceptions.ResourceNotFind("Command not exist")
    node_names = node_names[1:]

    manager = WorkspaceManager(name)
    manager.load()
    leaf = manager.find_command_tree_leaf(*node_names, leaf_name)
    if not leaf:
        raise exceptions.ResourceNotFind("Command not exist")
    cfg_editor = manager.load_cfg_editor_by_command(leaf)
    arg, _ = cfg_editor.find_arg_by_var(*node_names, leaf_name, arg_var=arg_var)
    if not arg:
        raise exceptions.ResourceNotFind("Argument not exist")

    if request.method == "GET":
        result = arg.to_primitive()
    elif request.method == "PATCH":
        data = request.get_json()
        cfg_editor.update_arg_by_var(*node_names, leaf_name, arg_var=arg_var, **data)
        manager.save()
        arg, _ = cfg_editor.find_arg_by_var(*node_names, leaf_name, arg_var=arg_var)
        result = arg.to_primitive()
    else:
        raise NotImplementedError()
    return jsonify(result)


# TODO: support to modify element of array or dict arguments
# @bp.route("/Workspaces/<name>/CommandTree/Nodes/<names_path:node_names>/Leaves/<name:leaf_name>/Arguments/<arg_var>/Element",
#           methods=("GET", "PATCH"))
# def editor_workspace_command_arg_element_of_array_or_dict(name, node_names, leaf_name, arg_var):
#     pass


@bp.route("/Workspaces/<name>/CommandTree/Nodes/<names_path:node_names>/Leaves/<name:leaf_name>/Arguments/<arg_var>/Flatten",
          methods=("POST", ))
def editor_workspace_command_argument_flatten(name, node_names, leaf_name, arg_var):
    if node_names[0] != WorkspaceManager.COMMAND_TREE_ROOT_NAME:
        raise exceptions.ResourceNotFind("Command not exist")
    node_names = node_names[1:]

    manager = WorkspaceManager(name)
    manager.load()
    leaf = manager.find_command_tree_leaf(*node_names, leaf_name)
    if not leaf:
        raise exceptions.ResourceNotFind("Command not exist")
    cfg_editor = manager.load_cfg_editor_by_command(leaf)

    # flatten argument variant
    arg, _ = cfg_editor.find_arg_by_var(*node_names, leaf_name, arg_var=arg_var)
    if not arg:
        raise exceptions.ResourceNotFind("Argument not exit")
    data = request.get_json()
    sub_args_options = data.get('subArgsOptions', None)
    cfg_editor.flatten_arg(*node_names, leaf_name, arg_var=arg_var, sub_args_options=sub_args_options)
    manager.save()

    return '', 200


@bp.route("/Workspaces/<name>/CommandTree/Nodes/<names_path:node_names>/Leaves/<name:leaf_name>/Arguments/<arg_var>/Unflatten",
          methods=("POST", ))
def editor_workspace_command_argument_unflatten(name, node_names, leaf_name, arg_var):
    if node_names[0] != WorkspaceManager.COMMAND_TREE_ROOT_NAME:
        raise exceptions.ResourceNotFind("Command not exist")
    node_names = node_names[1:]

    manager = WorkspaceManager(name)
    manager.load()
    leaf = manager.find_command_tree_leaf(*node_names, leaf_name)
    if not leaf:
        raise exceptions.ResourceNotFind("Command not exist")
    cfg_editor = manager.load_cfg_editor_by_command(leaf)

    parent, arg, _ = cfg_editor.find_arg_with_parent_by_var(*node_names, leaf_name, arg_var=arg_var)
    if arg:
        raise exceptions.ResourceConflict("Argument already exit")
    elif not parent:
        raise exceptions.ResourceNotFind("Argument not able to flatten")

    data = request.get_json()
    sub_args_options = data.get('subArgsOptions', None)
    cfg_editor.unflatten_arg(*node_names, leaf_name, arg_var=arg_var, options=data['options'], help=data['help'],
                             sub_args_options=sub_args_options)
    manager.save()
    arg, _ = cfg_editor.find_arg_by_var(*node_names, leaf_name, arg_var=arg_var)
    result = arg.to_primitive()

    return jsonify(result)


@bp.route("/Workspaces/<name>/CommandTree/Nodes/<names_path:node_names>/Leaves/<name:leaf_name>/Arguments/<arg_var>/UnwrapClass",
          methods=("POST", ))
def editor_workspace_command_argument_unwrap_class(name, node_names, leaf_name, arg_var):
    if node_names[0] != WorkspaceManager.COMMAND_TREE_ROOT_NAME:
        raise exceptions.ResourceNotFind("Command not exist")
    node_names = node_names[1:]

    manager = WorkspaceManager(name)
    manager.load()
    leaf = manager.find_command_tree_leaf(*node_names, leaf_name)
    if not leaf:
        raise exceptions.ResourceNotFind("Command not exist")
    cfg_editor = manager.load_cfg_editor_by_command(leaf)

    # unwrap argument variant
    arg, _ = cfg_editor.find_arg_by_var(*node_names, leaf_name, arg_var=arg_var)
    if not arg:
        raise exceptions.ResourceNotFind("Argument not exit")
    cfg_editor.unwrap_cls_arg(*node_names, leaf_name, arg_var=arg_var)
    manager.save()
    return '', 200


@bp.route("/Workspaces/<name>/CommandTree/Nodes/<names_path:node_names>/Leaves/<name:leaf_name>/Arguments/<arg_var>/FindSimilar",
          methods=("POST",))
def editor_workspace_command_argument_find_similar(name, node_names, leaf_name, arg_var):
    if node_names[0] != WorkspaceManager.COMMAND_TREE_ROOT_NAME:
        raise exceptions.ResourceNotFind("Command not exist")
    node_names = node_names[1:]

    manager = WorkspaceManager(name)
    manager.load()
    leaf = manager.find_command_tree_leaf(*node_names, leaf_name)
    if not leaf:
        raise exceptions.ResourceNotFind("Command not exist")
    cfg_editor = manager.load_cfg_editor_by_command(leaf)

    arg, _ = cfg_editor.find_arg_by_var(*node_names, leaf_name, arg_var=arg_var)
    if not arg:
        raise exceptions.ResourceNotFind("Argument not exist")

    result = {
        WorkspaceManager.COMMAND_TREE_ROOT_NAME: {
            "id": url_for('editor.editor_workspace_command_tree_node',
                          name=name,
                          node_names=[WorkspaceManager.COMMAND_TREE_ROOT_NAME])
        }
    }
    for cmd_names, args_map in manager.find_similar_args(*leaf.names, arg=arg).items():
        node = result[WorkspaceManager.COMMAND_TREE_ROOT_NAME]
        for idx, group_name in enumerate(cmd_names[:-1]):
            if 'commandGroups' not in node:
                node['commandGroups'] = {}
            if group_name not in node['commandGroups']:
                node['commandGroups'][group_name] = {
                    "id": url_for('editor.editor_workspace_command_tree_node',
                                  name=name,
                                  node_names=[WorkspaceManager.COMMAND_TREE_ROOT_NAME, *cmd_names[:idx+1]])
                }
            node = node['commandGroups'][group_name]
        if 'commands' not in node:
            node['commands'] = {}
        if cmd_names[-1] not in node['commands']:
            node['commands'][cmd_names[-1]] = {
                "id": url_for('editor.editor_workspace_command',
                              name=name,
                              node_names=[WorkspaceManager.COMMAND_TREE_ROOT_NAME, *cmd_names[:-1]],
                              leaf_name=cmd_names[-1]),
                "names": cmd_names,
                "args": {}
            }
        args = node['commands'][cmd_names[-1]]['args']
        for arg_var, arg_idx_list in args_map.items():
            if arg_var not in args:
                args[arg_var] = []
            args[arg_var].extend(arg_idx_list)
            args[arg_var] = sorted(set(args[arg_var]))
    return jsonify(result)


# command tree resource operations
@bp.route("/Workspaces/<name>/CommandTree/Nodes/<names_path:node_names>/AddSwagger", methods=("POST",))
def editor_workspace_tree_node_resources(name, node_names):
    if node_names[0] != WorkspaceManager.COMMAND_TREE_ROOT_NAME:
        raise exceptions.ResourceNotFind("Command group not exist")
    node_names = node_names[1:]
    if len(node_names) > 0:
        raise exceptions.InvalidAPIUsage("Not support to add resources under a specific node.")

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


@bp.route("/Workspaces/<name>/Resources/ReloadSwagger", methods=("POST",))
def editor_workspace_resource_reload_swagger(name):
    # update resource by reloading swagger
    manager = WorkspaceManager(name)
    manager.load()
    data = request.get_json()
    try:
        resources = data['resources']
    except KeyError:
        raise exceptions.InvalidAPIUsage("Invalid request")
    manager.reload_swagger_resources(resources=resources)
    manager.save()
    return "", 200


@bp.route("/Workspaces/<name>/Resources/<base64:resource_id>/V/<base64:version>", methods=("DELETE",))
def editor_workspace_resource(name, resource_id, version):
    # remove commands of the resource, including commands of subresources
    manager = WorkspaceManager(name)
    manager.load()
    if not manager.remove_resource(resource_id, version):
        return "", 204
    manager.save()
    return "", 200


@bp.route("/Workspaces/<name>/Resources/<base64:resource_id>/V/<base64:version>/Commands", methods=("GET",))
def list_workspace_resource_related_commands(name, resource_id, version):
    # list commands of the resource, including commands of sub resources
    manager = WorkspaceManager(name)
    manager.load()
    commands = manager.list_commands_by_resource(resource_id, version)
    result = [command.to_primitive() for command in commands]
    return jsonify(result)


@bp.route("/Workspaces/<name>/Resources/<base64:resource_id>/V/<base64:version>/Subresources", methods=("POST",))
def editor_workspace_subresources(name, resource_id, version):
    # add subresource command
    manager = WorkspaceManager(name)
    manager.load()
    data = request.get_json()
    try:
        arg_var = data['arg']
        cg_names = [nm for nm in data['commandGroupName'].split(' ') if nm]
        ref_args_options = data.get('refArgsOptions', None)
    except KeyError:
        raise exceptions.InvalidAPIUsage("Invalid request")
    manager.add_subresource_by_arg_var(resource_id, version, arg_var, cg_names, ref_args_options)
    manager.save()
    return "", 200


@bp.route("/Workspaces/<name>/Resources/<base64:resource_id>/V/<base64:version>/Subresources/<base64:subresource>", methods=("DELETE",))
def editor_workspace_subresource(name, resource_id, version, subresource):
    # Remove commands of subresource
    manager = WorkspaceManager(name)
    manager.load()
    if not manager.remove_subresource(resource_id, version, subresource):
        return "", 204
    manager.save()
    return "", 200


@bp.route("/Workspaces/<name>/Resources/<base64:resource_id>/V/<base64:version>/Subresources/<base64:subresource>/Commands", methods=("GET",))
def list_workspace_subresource_related_commands(name, resource_id, version, subresource):
    # list commands of subresource
    manager = WorkspaceManager(name)
    manager.load()
    commands = manager.list_commands_by_subresource(resource_id, version, subresource)
    result = [command.to_primitive() for command in commands]
    return jsonify(result)


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
