import os
from ._resource_provider import ResourceProvider


class SwaggerModule:

    def __init__(self, name, path, parent=None):
        self.name = name
        self._path = path
        self._parent = parent

    def __str__(self):
        if self._parent is not None:
            return f"{self._parent}/{self.name}"
        else:
            return f"{self.name}"


class MgmtPlaneModule(SwaggerModule):

    def __str__(self):
        if self._parent is None:
            return f'(MgmtPlane)/{super().__str__()}'
        else:
            return super(MgmtPlaneModule, self).__str__()

    def get_resource_providers(self):
        rp = []
        for name in os.listdir(self._path):
            path = os.path.join(self._path, name)
            if os.path.isdir(path):
                name_parts = name.split('.')
                if name_parts[0].lower() == 'microsoft':
                    readme_path = _search_readme_md_path(path, search_parent=True)
                    rp.append(ResourceProvider(name, path, readme_path, swagger_module=self))
                elif name.lower() != 'common':
                    # azsadmin module only
                    sub_module = MgmtPlaneModule(name, path, parent=self)
                    rp.extend(sub_module.get_resource_providers())
        return rp


class DataPlaneModule(SwaggerModule):

    def __str__(self):
        if self._parent is None:
            return f'(DataPlane)/{super().__str__()}'
        else:
            return super(DataPlaneModule, self).__str__()

    def get_resource_providers(self):
        rp = []
        for name in os.listdir(self._path):
            path = os.path.join(self._path, name)
            if os.path.isdir(path):
                if name.lower() in ('preview', 'stable'):
                    readme_path = _search_readme_md_path(self._path)
                    rp = [ResourceProvider(self.name, self._path, readme_path, swagger_module=self)]
                    break
                name_parts = name.split('.')
                if name_parts[0].lower() in ('microsoft', 'azure'):
                    readme_path = _search_readme_md_path(path, search_parent=True)
                    rp.append(ResourceProvider(name, path, readme_path, swagger_module=self))
                elif name.lower() != 'common':
                    has_sub_module = True
                    for sub_name in os.listdir(path):
                        sub_module_path = os.path.join(path, sub_name)
                        if os.path.isdir(sub_module_path) and sub_name.lower() in ('preview', 'stable'):
                            has_sub_module = False
                            break
                    if has_sub_module:
                        sub_module = DataPlaneModule(name, path, parent=self)
                        rp.extend(sub_module.get_resource_providers())
                    else:
                        readme_path = _search_readme_md_path(path, search_parent=True)
                        rp.append(ResourceProvider(name, path, readme_path, swagger_module=self))
        return rp


def _search_readme_md_path(path, search_parent=False):
    if search_parent:
        readme_path = os.path.join(os.path.dirname(path), 'readme.md')
        if os.path.exists(readme_path):
            return readme_path

    readme_path = os.path.join(path, 'readme.md')
    if os.path.exists(readme_path):
        return readme_path

    # find in sub directory
    for name in os.listdir(path):
        sub_path = os.path.join(path, name)
        if os.path.isdir(sub_path):
            readme_path = _search_readme_md_path(sub_path)
            if readme_path is not None:
                return readme_path
    return None
