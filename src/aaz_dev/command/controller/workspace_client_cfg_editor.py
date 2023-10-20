import logging
import os
import json

from .client_cfg_reader import ClientCfgReader
from command.model.configuration import CMDClientConfig

logger = logging.getLogger('backend')


class WorkspaceClientCfgEditor(ClientCfgReader):
    
    @staticmethod
    def get_cfg_path(ws_folder):
        path = os.path.join(ws_folder, 'client.json')
        return path

    @classmethod
    def load_client_cfg(cls, ws_folder):
        path = cls.get_cfg_path(ws_folder)
        if not os.path.exists(path):
            return None
        with open(path, 'r') as f:
            data = json.load(f)
        cfg = CMDClientConfig(data)
        cfg_editor = cls(cfg)
        cfg_editor.reformat()
        return cfg_editor

    def __init__(self, cfg):
        super().__init__(cfg)

    def reformat(self):
        self.cfg.reformat()
