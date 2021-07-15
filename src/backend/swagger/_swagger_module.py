import os
from ._utils import map_path_2_repo
from ._resource_provider import ResourceProvider


def search_readme_md_path(path):
    readme_path = os.path.join(path, 'readme.md')
    if os.path.exists(readme_path):
        return readme_path

    # find in sub directory
    for name in os.listdir(path):
        sub_path = os.path.join(path, name)
        if os.path.isdir(sub_path):
            readme_path = search_readme_md_path(sub_path)
            if readme_path is not None:
                return readme_path
    return None


class SwaggerModule:

    def __init__(self, name, path, parent=None):
        self.name = name
        self._path = path
        self._parent = parent

    def __str__(self):
        if self._parent is not None:
            return f"{self._parent.name}/{self.name}"
        else:
            return f"{self.name}"


class MgmtPlanModule(SwaggerModule):

    def __init__(self, name, path, parent=None):
        super().__init__(name, path, parent)

    def __str__(self):
        return f'{super().__str__()}(Mgmt)'

    def get_resource_providers(self):
        rp = []
        for name in os.listdir(self._path):
            path = os.path.join(self._path, name)
            if os.path.isdir(path):
                name_parts = name.split('.')
                if name_parts[0].lower() == 'microsoft':
                    readme_path = search_readme_md_path(self._path)
                    rp.append(ResourceProvider(name, path, readme_path, swagger_module=self))
                elif name != 'common':
                    # azsadmin module only
                    sub_module = MgmtPlanModule(name, path, parent=self)
                    rp.extend(sub_module.get_resource_providers())
        return rp


class DataPlanModule(SwaggerModule):

    def __init__(self, name, path):
        super().__init__(name, path)

    def __str__(self):
        return f'{super().__str__()}(Data)'

    @property
    def _readme_path(self):
        return os.path.join(self._path, 'readme.md')

    def get_resource_providers(self):
        rp = []
        if os.path.exists(self._readme_path):
            print(f'{map_path_2_repo(self._path)}')
        # for name in os.listdir(self._path):
        #     path = os.path.join(self._path, name)
        #     if os.path.isdir(path):
        #         name_parts = name.split('.')
        #         if len(name_parts) != 2 or name_parts[0].lower() != 'microsoft':
        #             print(f'{self}:\t{map_path_2_repo(path)}')
        #             continue
        #         rp.append(name)
        return rp
