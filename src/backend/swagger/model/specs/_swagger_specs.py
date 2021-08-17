import os
from ._swagger_module import MgmtPlaneModule, DataPlaneModule


class SwaggerSpecs:

    def __init__(self, folder_path):
        # TODO: check folder structures
        self._folder_path = folder_path

    @property
    def _spec_folder_path(self):
        return os.path.join(self._folder_path, 'specification')

    def get_mgmt_plane_modules(self):
        modules = []
        for name in os.listdir(self._spec_folder_path):
            path = os.path.join(self._spec_folder_path, name, 'resource-manager')
            if os.path.isdir(path):
                modules.append(MgmtPlaneModule(name, path=path))
        return modules

    def get_data_plane_modules(self):
        modules = []
        for name in os.listdir(self._spec_folder_path):
            path = os.path.join(self._spec_folder_path, name, 'data-plane')
            if os.path.isdir(path):
                modules.append(DataPlaneModule(name, path=path))
        return modules
