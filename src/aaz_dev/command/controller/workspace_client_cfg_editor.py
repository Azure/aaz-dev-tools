import logging
import os
import json
from datetime import datetime

from .client_cfg_reader import ClientCfgReader
from .workspace_helper import ArgumentUpdateMixin
from command.model.configuration import CMDClientConfig, CMDDiffLevelEnum

logger = logging.getLogger('backend')


class WorkspaceClientCfgEditor(ClientCfgReader, ArgumentUpdateMixin):
    
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

    @classmethod
    def new_client_cfg(cls, plane, templates, auth, ref_cfg: ClientCfgReader = None):
        cfg = CMDClientConfig(raw_data={
            "plane": plane,
            "endpoints": {
                "templates": templates
            },
            "auth": auth
        })
        cfg.endpoints.generate_params()
        ref_args = ref_cfg.cfg.arg_group.args if ref_cfg else None
        cfg.generate_args(ref_args=ref_args)
        if not ref_cfg or cfg.endpoints.diff(ref_cfg.cfg.endpoints, CMDDiffLevelEnum.Structure) or cfg.auth.diff(ref_cfg.cfg.auth, CMDDiffLevelEnum.Structure):
            # when endpoints or auth changed then bump up version
            cfg.version = datetime.utcnow()
        else:
            cfg.version = ref_cfg.cfg.version

        cfg_editor = cls(cfg)
        cfg_editor.reformat()
        return cfg_editor

    def __init__(self, cfg):
        super().__init__(cfg)

    def reformat(self):
        self.cfg.reformat()

    def update_arg_by_var(self, arg_var, **kwargs):
        arg = self.find_arg_by_var(arg_var=arg_var)
        if not arg:
            return None
        self._update_arg(arg, **kwargs)
        self.cfg.version = datetime.utcnow()
        self.reformat()
