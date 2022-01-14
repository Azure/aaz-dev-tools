from flask import Blueprint, jsonify, request, url_for
from command.controller.config_editor import ConfigEditorWorkspaceManager, WorkspaceEditor
from utils import exceptions
import os

bp = Blueprint('editor', __name__, url_prefix='/aaz/editor')


@bp.route("/workspaces", methods=("GET", "POST"))
def editor_workspaces():
    if request.method == "POST":
        # create a new workspace
        # the name of workspace is required
        data = request.get_json()
        if not data or not isinstance(data, dict) or 'name' not in data or 'plane' not in data:
            raise exceptions.InvalidAPIUsage("Invalid request body")
        name = data['name']
        plane = data['plane']
        workspace = ConfigEditorWorkspaceManager.create_workspace(name, plane)
        result = workspace.to_primitive()
        path = ConfigEditorWorkspaceManager.get_ws_json_file_path(name)
        result.update({
            'url': url_for('editor.editor_workspace', name=workspace.name),
            'file': path,
            'updated': os.path.getmtime(path)
        })
    elif request.method == "GET":
        result = []
        for ws in ConfigEditorWorkspaceManager.list_workspaces():
            result.append({
                **ws,
                'url': url_for('editor.editor_workspace', name=ws['name']),
            })
    else:
        raise NotImplementedError(request.method)

    return jsonify(result)


@bp.route("/workspaces/<name>", methods=("GET", "DELETE"))
def editor_workspace(name):
    if request.method == "GET":
        workspace = ConfigEditorWorkspaceManager.load_workspace(name)
    # elif request.method == "PUT":
    #     data = request.get_json()
    #     if not isinstance(data, dict):
    #         raise exceptions.InvalidAPIUsage("invalid workspace data format")
    #     data = dict((k, v) for k, v in data.items() if k not in ['file', 'url', 'updated'])
    #     workspace = CMDEditorWorkspace(data)
    #     workspace = ConfigEditorWorkspaceManager.update_workspace(name, workspace)
    elif request.method == "DELETE":
        if ConfigEditorWorkspaceManager.delete_workspace(name):
            return '', 200
        else:
            return '', 204  # resource not found
    else:
        raise NotImplementedError()

    result = workspace.to_primitive()
    path = ConfigEditorWorkspaceManager.get_ws_json_file_path(name)
    result.update({
        'url': url_for('editor.editor_workspace', name=workspace.name),
        'file': path,
        'updated': os.path.getmtime(path)
    })
    return jsonify(result)


# TODO: command tree operations
@bp.route("/workspace/<name>/commandTree/nodes/<path:command_group>", methods=("PUT", "DELETE"))
def editor_workspace_command_tree_node(name, command_group):
    pass


@bp.route("/workspace/<name>/commandTree/nodes/<path:command_group>/rename", methods=("POST", ))
def editor_workspace_command_tree_node_rename(name, command_group):
    pass


@bp.route("/workspace/<name>/commandTree/leaf/<path:command>", methods=("GET", "PUT"))
def editor_workspace_command(name, command):
    # get the command configuration
    # put update the command configuration
    pass


@bp.route("/workspace/<name>/commandTree/leaf/<path:command>/rename", methods=("POST", ))
def editor_workspace_command_rename(name, command):
    pass


# resource operations
@bp.route("/workspace/<name>/resources", methods=("GET", "POST"))
def editor_workspace_resources(name):
    if request.method == "POST":
        # add new resource
        data = request.get_json()
        if "swagger" in data and "aaz" in data:
            raise exceptions.InvalidAPIUsage("Please add aaz resources and call reload swagger api")
        elif "swagger" in data:
            try:
                plane = data['swagger']['plane']
                mod_names = data['swagger']['module']
                version = data['swagger']['version']
                resource_ids = data['swagger']['resources']
            except KeyError:
                raise exceptions.InvalidAPIUsage("invalid request")
            editor = WorkspaceEditor(name)
            editor.add_resources_by_swagger(
                plane=plane,
                mod_names=mod_names,
                version=version,
                resource_ids=resource_ids,
            )
        elif "aaz" in data:
            try:
                plane = data['swagger']['plane'],
                version = data['swagger']['version'],
                resource_ids = data['swagger']['resources']
            except KeyError:
                raise exceptions.InvalidAPIUsage("invalid request")
            editor = WorkspaceEditor(name)
            editor.add_resources_by_aaz(
                plane=plane,
                version=version,
                resource_ids=resource_ids,
            )
        else:
            raise exceptions.InvalidAPIUsage("invalid request")
    elif request.method == "GET":
        # TODO: return the resource list
        workspace = ConfigEditorWorkspaceManager.load_workspace(name)
        pass
    else:
        raise NotImplementedError(request.method)


@bp.route("/workspace/<name>/resources/<resource_id>/v/<version>", methods=("GET", "PUT", "DELETE"))
def editor_workspace_resource(name, resource_id, version):
    if request.method == "GET":
        # return the resource configuration
        pass
    elif request.method == "PUT":
        # update the resource configuration
        pass
    elif request.method == "DELETE":
        # delete the resource configuration
        pass
    else:
        raise NotImplementedError(request.method)


@bp.route("/workspace/<name>/resources/reloadSwagger", methods=("POST",))
def editor_workspace_resource_reload_swagger(name):
    # update resource by reloading swagger
    data = request.get_json()
    # data = (resource_id, swagger_version)
    # TODO:


@bp.route("/workspace/<name>/generate", methods=("POST", ))
def editor_workspace_generate(name):
    # generate code and command configurations in cli repos and aaz repo
    raise NotImplementedError()


@bp.route("/workspace/<name>/try", methods=("POST", ))
def editor_workspace_try_cli(name):
    # try current commands by installed as a try extension of cli
    raise NotImplementedError()
