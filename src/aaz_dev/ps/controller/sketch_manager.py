import json
import logging
import os
import shutil
from datetime import datetime

from swagger.controller.specs_manager import SwaggerSpecsManager
from command.controller.specs_manager import AAZSpecsManager
from cli.model.view import CLIViewProfile
from utils.config import Config

logger = logging.getLogger('backend')

class SketchManager:

    IN_MEMORY = "__IN_MEMORY_SKETCH__"

    @classmethod
    def list_sketches(cls):
        sketches = []
        if not os.path.exists(Config.AAZ_DEV_SKETCH_FOLDER):
            return sketches
        
        for name in os.listdir(Config.AAZ_DEV_SKETCH_FOLDER):
            if not os.path.isdir(os.path.join(Config.AAZ_DEV_SKETCH_FOLDER, name)):
                continue
            manager = cls(name)
            if os.path.exists(manager.path) and os.path.isfile(manager.path):
                sketches.append({
                    "name": name,
                    "folder": os.path.join(Config.AAZ_DEV_SKETCH_FOLDER, name),
                    "updated": os.path.getmtime(os.path.join(Config.AAZ_DEV_SKETCH_FOLDER, name))
                })
        return sketches
    
    @classmethod
    def new(cls, name, ps_module_name, selected_resource_providers, cli_profile: CLIViewProfile, **kwargs):
        pass

    def __init__(self, name, folder=None):
        self.name = name
        if not folder:
            if not Config.AAZ_DEV_SKETCH_FOLDER or os.path.exists(Config.AAZ_DEV_SKETCH_FOLDER) and not os.path.isdir(Config.AAZ_DEV_SKETCH_FOLDER):
                raise ValueError(f"Invalid AAZ_DEV_SKETCH_FOLDER: Expect a folder path: {Config.AAZ_DEV_SKETCH_FOLDER}")
            self.folder = os.path.join(Config.AAZ_DEV_SKETCH_FOLDER, name)
        else:
            self.folder = os.path.expanduser(folder) if folder != self.IN_MEMORY else self.IN_MEMORY
        
        if not self.is_in_memory and os.path.exists(self.folder) and not os.path.isdir(self.folder):
            raise ValueError(f"Invalid sketch folder: Expect a folder path: {self.folder}")
        self.path = os.path.join(self.folder, 'sketch.json')

        self.sketch = None
        self._cfg_editors = {}

    @property
    def is_in_memory(self):
        return self.folder == self.IN_MEMORY

    @property
    def aaz_specs(self):
        if not self._aaz_specs:
            self._aaz_specs = AAZSpecsManager()
        return self._aaz_specs

    @property
    def swagger_specs(self):
        if not self._swagger_specs:
            self._swagger_specs = SwaggerSpecsManager()
        return self._swagger_specs
