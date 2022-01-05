import os

from ._swagger_module import MgmtPlaneModule, DataPlaneModule


class SwaggerSpecs:

    def __init__(self, folder_path):
        self._folder_path = folder_path

    @property
    def _spec_folder_path(self):
        return os.path.join(self._folder_path, 'specification')

    def get_mgmt_plane_modules(self):
        modules = []
        for name in os.listdir(self._spec_folder_path):
            module = self.get_mgmt_plane_module(name)
            if module:
                modules.append(module)
        return modules

    def get_mgmt_plane_module(self, *names):
        if not names:
            return None
        name = names[0]
        path = os.path.join(self._spec_folder_path, name, 'resource-manager')
        if not os.path.isdir(path):
            return None
        module = MgmtPlaneModule(name, folder_path=path)
        for name in names[1:]:
            path = os.path.join(path, name)
            if not os.path.isdir(path):
                return None
            module = MgmtPlaneModule(name, folder_path=path, parent=module)
        return module

    def get_data_plane_modules(self):
        modules = []
        for name in os.listdir(self._spec_folder_path):
            module = self.get_data_plane_module(name)
            if module:
                modules.append(module)
        return modules

    def get_data_plane_module(self, *names):
        if not names:
            return None
        name = names[0]
        path = os.path.join(self._spec_folder_path, name, 'data-plane')
        if not os.path.isdir(path):
            return None
        module = DataPlaneModule(name, folder_path=path)
        for name in names[1:]:
            path = os.path.join(path, name)
            if not os.path.isdir(path):
                return None
            module = DataPlaneModule(name, folder_path=path, parent=module)
        return module
