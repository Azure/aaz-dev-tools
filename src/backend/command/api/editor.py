from flask import Blueprint, jsonify, request, url_for
from command.controller.config_editor import ConfigEditorWorkspaceManager
from command.model.editor import CMDEditorWorkspace
from utils import exceptions
import os

bp = Blueprint('editor', __name__, url_prefix='/command/editor')


@bp.route("/workspaces", methods=("Get", "Post"))
def editor_workspaces():
    if request.method == "POST":
        # create a new workspace
        # the name of workspace is required
        data = request.get_json()
        if not data or not isinstance(data, dict) or 'name' not in data:
            raise exceptions.InvalidAPIUsage("Invalid request body")
        name = data['name']
        workspace = ConfigEditorWorkspaceManager.create_workspace(name)
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


@bp.route("/workspaces/<name>", methods=("Get", "Put", "Delete"))
def editor_workspace(name):
    if request.method == "GET":
        workspace = ConfigEditorWorkspaceManager.load_workspace(name)
    elif request.method == "PUT":
        data = request.get_json()
        if not isinstance(data, dict):
            raise exceptions.InvalidAPIUsage("invalid workspace data format")
        data = dict((k, v) for k, v in data.items() if k not in ['file', 'url', 'updated'])
        workspace = CMDEditorWorkspace(data)
        workspace = ConfigEditorWorkspaceManager.update_workspace(name, workspace)
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


@bp.route("/workspace/<name>/generate", methods=("Post", ))
def editor_workspace_generate(name):
    # generate code and command configurations in cli repos and aaz repo
    raise NotImplementedError()


@bp.route("/workspace/<name>/try", methods=("Post", ))
def editor_workspace_try_cli(name):
    # try current commands by installed as a try extension of cli
    raise NotImplementedError()
