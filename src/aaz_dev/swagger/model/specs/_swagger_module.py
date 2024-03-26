import os

from utils.plane import PlaneEnum
from ._resource_provider import OpenAPIResourceProvider, TypeSpecResourceProvider
from ._typespec_helper import TypeSpecHelper


class SwaggerModule:

    def __init__(self, plane, name, folder_path, parent=None):
        assert plane == PlaneEnum.Mgmt or PlaneEnum.is_data_plane(plane), f"Invalid plane: '{plane}'"
        self.plane = plane
        self.name = name
        self.folder_path = folder_path
        self._parent = parent

    def __str__(self):
        if self._parent is not None:
            return f"{self._parent}/{self.name}"
        else:
            return f"{self.name}"

    def __eq__(self, other):
        return isinstance(other, self.__class__) and str(other) == str(self)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(str(self))

    @property
    def names(self):
        if self._parent is None:
            return [self.name]
        else:
            return [*self._parent.names, self.name]


class MgmtPlaneModule(SwaggerModule):

    def __str__(self):
        if self._parent is None:
            return f'{self.plane}/{super().__str__()}'
        else:
            return super(MgmtPlaneModule, self).__str__()

    def get_resource_providers(self):
        rp = []
        rp.extend(self._get_openapi_resource_providers())
        rp.extend(self._get_typespec_resource_providers())
        return rp

    def _get_openapi_resource_providers(self):
        rp = []
        if 'resource-manager' not in self.folder_path:
            folder_path = os.path.join(self.folder_path, 'resource-manager')
        else:
            # ignore to add resource-manager folder for sub openapi modules
            folder_path = self.folder_path
        if not os.path.exists(folder_path):
            return rp
        for name in os.listdir(folder_path):
            path = os.path.join(folder_path, name)
            if os.path.isdir(path):
                name_parts = name.split('.')
                if len(name_parts) >= 2:
                    readme_path = _search_readme_md_path(path, search_parent=True)
                    rp.append(OpenAPIResourceProvider(name, path, readme_path, swagger_module=self))
                elif name.lower() != 'common':
                    # azsadmin module only
                    sub_module = MgmtPlaneModule(plane=self.plane, name=name, folder_path=path, parent=self)
                    rp.extend(sub_module.get_resource_providers())
        return rp

    def _get_typespec_resource_providers(self):
        rp = {}
        if 'resource-manager' in self.folder_path:
            return rp

        for namespace, ts_path, cfg_path in TypeSpecHelper.find_mgmt_plane_entry_files(self.folder_path):
            entry_folder = os.path.dirname(ts_path)
            if namespace in rp:
                rp[namespace].entry_folders.append(entry_folder)
            else:
                rp[namespace] = TypeSpecResourceProvider(
                    name=namespace, entry_folders=[entry_folder], swagger_module=self)
        return [*rp.values()]


class DataPlaneModule(SwaggerModule):

    def __str__(self):
        if self._parent is None:
            return f'{self.plane}/{super().__str__()}'
        else:
            return super(DataPlaneModule, self).__str__()

    def get_resource_providers(self):
        rp = []
        rp.extend(self._get_openapi_resource_providers())
        rp.extend(self._get_typespec_resource_providers())
        scope = PlaneEnum.get_data_plane_scope(self.plane)
        if scope:
            rp = [r for r in rp if r.name.lower() == scope]
        return rp

    def _get_openapi_resource_providers(self):
        rp = []
        if 'data-plane' not in self.folder_path:
            folder_path = os.path.join(self.folder_path, 'data-plane')
        else:
            # ignore to add data-plane folder for sub openapi modules
            folder_path = self.folder_path
        if not os.path.exists(folder_path):
            return rp
        for name in os.listdir(folder_path):
            path = os.path.join(folder_path, name)
            if os.path.isdir(path):
                if name.lower() in ('preview', 'stable'):
                    continue
                name_parts = name.split('.')
                if len(name_parts) >= 2:
                    readme_path = _search_readme_md_path(path, search_parent=True)
                    rp.append(OpenAPIResourceProvider(name, path, readme_path, swagger_module=self))
                elif name.lower() != 'common':
                    sub_module = DataPlaneModule(plane=self.plane, name=name, folder_path=path, parent=self)
                    rp.extend(sub_module.get_resource_providers())
        return rp

    def _get_typespec_resource_providers(self):
        rp = {}
        if 'resource-manager' in self.folder_path:
            return rp

        for namespace, ts_path, cfg_path in TypeSpecHelper.find_data_plane_entry_files(self.folder_path):
            entry_folder = os.path.dirname(ts_path)
            if namespace in rp:
                rp[namespace].entry_folders.append(entry_folder)
            else:
                rp[namespace] = TypeSpecResourceProvider(
                    name=namespace, entry_folders=[entry_folder], swagger_module=self)
        return [*rp.values()]


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
