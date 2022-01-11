from command.model.configuration import CMDResource, CMDConfiguration
from command.model.editor import CMDEditorWorkspace
from utils.config import Config
import os
import json
from utils import exceptions
from datetime import datetime


class ConfigEditorWorkspaceManager:

    @staticmethod
    def get_ws_folder():
        if not os.path.exists(Config.AAZ_DEV_WORKSPACE_FOLDER):
            os.makedirs(Config.AAZ_DEV_WORKSPACE_FOLDER, exist_ok=True)
        if not os.path.isdir(Config.AAZ_DEV_WORKSPACE_FOLDER):
            raise ValueError(
                f"Invalid AAZ_DEV_WORKSPACE_FOLDER: Expect a folder path: {Config.AAZ_DEV_WORKSPACE_FOLDER}")
        return Config.AAZ_DEV_WORKSPACE_FOLDER

    @staticmethod
    def get_ws_file_name(name):
        return f'{name}.ws.json'

    @classmethod
    def get_ws_file_path(cls, name):
        workspace_folder = cls.get_ws_folder()
        return os.path.join(workspace_folder, cls.get_ws_file_name(name))

    @classmethod
    def list_workspaces(cls):
        workspaces = []
        workspace_folder = cls.get_ws_folder()
        for file_name in os.listdir(workspace_folder):
            if file_name.endswith('.ws.json'):
                name = file_name[:-(len('.ws.json'))]
                path = os.path.join(workspace_folder, file_name)
                workspaces.append({
                    "name": name,
                    "file": path,
                    "updated": os.path.getmtime(path)
                })
        return workspaces

    @classmethod
    def load_workspace(cls, name):
        # TODO: handle exceptions
        path = cls.get_ws_file_path(name)
        if not os.path.exists(path) or not os.path.isfile(path):
            raise exceptions.ResourceNotFind(f"Workspace file not exist: {path}")
        with open(path, 'r') as f:
            data = json.load(f)
            ws = CMDEditorWorkspace(raw_data=data)
        return ws

    @classmethod
    def save_workspace(cls, path, ws):
        ws_data = ws.to_primitive()
        with open(path, 'w') as f:
            json.dump(ws_data, f, ensure_ascii=False)

    @classmethod
    def delete_workspace(cls, name):
        path = cls.get_ws_file_path(name)
        if os.path.exists(path):
            if not os.path.isfile(path):
                raise exceptions.ResourceConflict(f"Workspace conflict: Is not file path: {path}")
            os.remove(path)
            return True
        return False

    @classmethod
    def create_workspace(cls, name):
        path = cls.get_ws_file_path(name)
        if os.path.exists(path):
            raise exceptions.ResourceConflict(f"Workspace conflict: File path exists: {path}")
        ws = CMDEditorWorkspace({
            "name": name,
            "version": datetime.utcnow(),
        })
        cls.save_workspace(path, ws)
        return ws

    @classmethod
    def update_workspace(cls, name, ws):
        path = cls.get_ws_file_path(name)
        pre_ws = cls.load_workspace(name)
        if pre_ws.version != ws.version:
            raise exceptions.ResourceConflict(
                f"Workspace conflict: Version control timestamp not match: expect {pre_ws.version} get {ws.version}")
        ws.version = datetime.utcnow()
        cls.save_workspace(path, ws)
        return ws


class CommandConfigEditor:

    def __init__(self, workspace):
        self.workspace = workspace

    def _load_cmd_config(self, config_path):
        # load command configuration from persistence layer
        return None

    def _fetch_config_path_by_resource_id(self, resource_id, v):
        # TODO: read from repo index
        return None

    def _fetch_config_path_by_cmd_name(self, cmd_name, v):
        # TODO: read from repo index
        return None

    def add_resource_by_cmd(self, cmd_name, v):
        config_path = self._fetch_config_path_by_cmd_name(cmd_name, v)
        cmd_config = self._load_cmd_config(config_path)
        # TODO:

    def add_resource_by_swagger(self, module, resource_id, v, inherent_v=None):
        # config_path = self._fetch_config_path_by_resource_id(resource_id, v)
        resources = [
            CMDResource({
                "id": resource_id,
                "version": v
            })
        ]
        if inherent_v:
            config_path = self._fetch_config_path_by_resource_id(resource_id, inherent_v)
            assert config_path is not None, "config not exist error"
            inherent_config = self._load_cmd_config(config_path)    # type: CMDConfiguration
            resources = inherent_config.resources   # use inherent configuration resources





