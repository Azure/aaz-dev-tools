from command.model.editor import CMDEditorWorkspace
from utils.config import Config
import os
import json
from utils import exceptions
from datetime import datetime
import shutil


class ConfigEditorWorkspaceManager:

    @staticmethod
    def get_ws_folder(name):
        if os.path.exists(Config.AAZ_DEV_WORKSPACE_FOLDER) and not os.path.isdir(Config.AAZ_DEV_WORKSPACE_FOLDER):
            raise ValueError(
                f"Invalid AAZ_DEV_WORKSPACE_FOLDER: Expect a folder path: {Config.AAZ_DEV_WORKSPACE_FOLDER}")
        ws_folder = os.path.join(Config.AAZ_DEV_WORKSPACE_FOLDER, name)
        return ws_folder

    @classmethod
    def get_ws_json_file_path(cls, name):
        ws_folder = cls.get_ws_folder(name)
        if os.path.exists(ws_folder) and not os.path.isdir(ws_folder):
            raise ValueError(f"Invalid workspace folder: Expect a folder path: {ws_folder}")
        return os.path.join(ws_folder, 'ws.json')

    @classmethod
    def list_workspaces(cls):
        workspaces = []
        if not os.path.exists(Config.AAZ_DEV_WORKSPACE_FOLDER):
            return workspaces

        for name in os.listdir(Config.AAZ_DEV_WORKSPACE_FOLDER):
            if not os.path.isdir(os.path.join(Config.AAZ_DEV_WORKSPACE_FOLDER, name)):
                continue
            path = cls.get_ws_json_file_path(name)
            if os.path.exists(path) and os.path.isfile(path):
                workspaces.append({
                    "name": name,
                    "file": path,
                    "updated": os.path.getmtime(path)
                })
        return workspaces

    @classmethod
    def load_workspace(cls, name):
        # TODO: handle exceptions
        path = cls.get_ws_json_file_path(name)
        if not os.path.exists(path) or not os.path.isfile(path):
            raise exceptions.ResourceNotFind(f"Workspace json file not exist: {path}")
        with open(path, 'r') as f:
            data = json.load(f)
            ws = CMDEditorWorkspace(raw_data=data)
        return ws

    @classmethod
    def save_workspace(cls, name, ws):
        folder = cls.get_ws_folder(name)
        path = cls.get_ws_json_file_path(name)
        if not os.path.exists(folder):
            os.makedirs(folder)
        ws_data = ws.to_primitive()
        with open(path, 'w') as f:
            json.dump(ws_data, f, ensure_ascii=False)

    @classmethod
    def delete_workspace(cls, name):
        folder = cls.get_ws_folder(name)
        path = cls.get_ws_json_file_path(name)
        if os.path.exists(path):
            # make sure ws.json exist in folder
            if not os.path.isfile(path):
                raise exceptions.ResourceConflict(f"Workspace conflict: Is not file path: {path}")
            shutil.rmtree(folder)   # remove the whole folder
            return True
        return False

    @classmethod
    def create_workspace(cls, name):
        path = cls.get_ws_json_file_path(name)
        if os.path.exists(path):
            raise exceptions.ResourceConflict(f"Workspace conflict: Workspace json file path exists: {path}")
        ws = CMDEditorWorkspace({
            "name": name,
            "version": datetime.utcnow(),
        })
        cls.save_workspace(name, ws)
        return ws

    @classmethod
    def update_workspace(cls, name, ws):
        pre_ws = cls.load_workspace(name)
        if pre_ws.version != ws.version:
            raise exceptions.ResourceConflict(
                f"Workspace conflict: Version control timestamp not match: expect {pre_ws.version} get {ws.version}")
        ws.version = datetime.utcnow()
        cls.save_workspace(name, ws)
        return ws


class CommandConfigEditor:

    def __init__(self, workspace):
        self.workspace = workspace
    
    def add_resource_by_swagger(self):
        pass

    def add_resource_by_cmd(self):
        pass


    # def _load_cmd_config(self, config_path):
    #     # load command configuration from persistence layer
    #     return None
    #
    # def _fetch_config_path_by_resource_id(self, resource_id, v):
    #     # TODO: read from repo index
    #     return None
    #
    # def _fetch_config_path_by_cmd_name(self, cmd_name, v):
    #     # TODO: read from repo index
    #     return None
    #
    # def add_resource_by_cmd(self, cmd_name, v):
    #     config_path = self._fetch_config_path_by_cmd_name(cmd_name, v)
    #     cmd_config = self._load_cmd_config(config_path)
    #     # TODO:
    #
    # def add_resource_by_swagger(self, module, resource_id, v, inherent_v=None):
    #     # config_path = self._fetch_config_path_by_resource_id(resource_id, v)
    #     resources = [
    #         CMDResource({
    #             "id": resource_id,
    #             "version": v
    #         })
    #     ]
    #     if inherent_v:
    #         config_path = self._fetch_config_path_by_resource_id(resource_id, inherent_v)
    #         assert config_path is not None, "config not exist error"
    #         inherent_config = self._load_cmd_config(config_path)    # type: CMDConfiguration
    #         resources = inherent_config.resources   # use inherent configuration resources
    #




