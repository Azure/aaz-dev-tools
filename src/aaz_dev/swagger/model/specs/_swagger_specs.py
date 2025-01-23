import os

from utils.plane import PlaneEnum
from utils.exceptions import ResourceNotFind, InvalidAPIUsage
from ._swagger_module import MgmtPlaneModule, DataPlaneModule
from ._typespec_helper import TypeSpecHelper


class SwaggerSpecs:

    def __init__(self, folder_path):
        self._folder_path = folder_path
        # self._repo_name = self._get_repo_name()
        # self._remote_name = self._get_upstream_remote_name()

    @property
    def spec_folder_path(self):
        return os.path.join(self._folder_path, 'specification')

    def get_mgmt_plane_modules(self, plane):
        modules = []
        for name in os.listdir(self.spec_folder_path):
            module = self.get_mgmt_plane_module(name, plane=plane)
            if module:
                modules.append(module)
        return modules

    def get_mgmt_plane_module(self, *names, plane):
        if not names:
            return None
        name = names[0]
        if not PlaneEnum.is_valid_swagger_module(plane=plane, module_name=name):
            return None

        path = os.path.join(self.spec_folder_path, name)
        if not os.path.isdir(path):
            return None
        if os.path.isdir(os.path.join(path, 'resource-manager')) or TypeSpecHelper.find_mgmt_plane_entry_files(path):
            module = MgmtPlaneModule(plane=plane, name=name, folder_path=path)
            for name in names[1:]:
                path = os.path.join(path, name)
                if not os.path.isdir(path):
                    return None
                module = MgmtPlaneModule(plane=plane, name=name, folder_path=path, parent=module)
            return module
        return None

    def get_data_plane_modules(self, plane):
        modules = []
        for name in os.listdir(self.spec_folder_path):
            module = self.get_data_plane_module(name, plane=plane)
            if module:
                modules.append(module)
        return modules

    def get_data_plane_module(self, *names, plane):
        if not names:
            return None
        name = names[0]
        if not PlaneEnum.is_valid_swagger_module(plane=plane, module_name=name):
            return None

        path = os.path.join(self.spec_folder_path, name)
        if os.path.isdir(os.path.join(path, 'data-plane')) or TypeSpecHelper.find_data_plane_entry_files(path):
            module = DataPlaneModule(plane=plane, name=name, folder_path=path)
            for name in names[1:]:
                path = os.path.join(path, name)
                if not os.path.isdir(path):
                    return None
                module = DataPlaneModule(plane=plane, name=name, folder_path=path, parent=module)
            return module
        return None
    
    # def _get_repo_name(self):
    #     # get repo name from origin remote
    #     git_config_path = os.path.join(self._folder_path, '.git', 'config')
    #     if not os.path.exists(git_config_path):
    #         return None

    #     in_origin_remote = False

    #     with open(git_config_path, 'r') as f:
    #         for line in f:
    #             line = line.strip()
    #             if line.startswith('[remote "origin"]'):
    #                 in_origin_remote = True
    #             elif in_origin_remote and line.startswith('url'):
    #                 url = line.split('=', maxsplit=1)[1].strip()
    #                 return url.split('/')[-1].split('.')[0]
    #     return None
    
    # def _get_upstream_remote_name(self):
    #     git_config_path = os.path.join(self._folder_path, '.git', 'config')
        
    #     if not self._repo_name:
    #         return None

    #     if not os.path.exists(git_config_path):
    #         return None
        
    #     remote_name = None
        
    #     with open(git_config_path, 'r') as f:
    #         current_remote = None
    #         for line in f:
    #             line = line.strip()
    #             if line.startswith('[remote "'):
    #                 current_remote = line[9:-2]  # Extract remote name between quotes
    #             elif line.startswith('url') and current_remote:
    #                 url = line.split('=', maxsplit=1)[1].strip()
    #                 # Check for both HTTPS and git@ formats
    #                 if (url == f"git@github.com:Azure/{self._repo_name}.git" or
    #                     url == f"https://github.com/Azure/{self._repo_name}.git"):
    #                     remote_name = current_remote
    #                     break
    #     return remote_name

    # def fetch_upstream(self, branch_name):
    #     if not self._remote_name:
    #         raise InvalidAPIUsage(f"Cannot find upstream for {self._repo_name} please run ` git -C {self._folder_path} remote add upstream https://github.com/Azure/{self._repo_name}.git`")

    #     try:
    #         subprocess.run(args=["git", "-C", self._folder_path, "fetch", self._remote_name, branch_name], shell=False, check=True)
    #     except Exception as e:
    #         raise InvalidAPIUsage(f"Failed to fetch upstream for {self._repo_name} please run `git -C {self._folder_path} fetch {self._remote_name} {branch_name}`")

    # def get_commit_hash_from_upstream(self, branch_name):
    #     # First ensure we have the latest upstream branch
    #     self.fetch_upstream(branch_name)
    #     try:
    #         # Get the merge-base commit (common ancestor) between HEAD and upstream branch
    #         result = subprocess.run(
    #             ["git", "-C", self._folder_path, "merge-base", "HEAD", f"{self._remote_name}/{branch_name}"],
    #             capture_output=True,
    #             text=True,
    #             check=True
    #         )
    #         return result.stdout.strip()
    #     except subprocess.CalledProcessError as e:
    #         raise InvalidAPIUsage(f"Failed to get commit hash: {e.stderr}")


class SingleModuleSwaggerSpecs:

    def __init__(self, folder_path, module_name):
        if not os.path.isdir(folder_path):
            raise ValueError(f"Path not exist: {folder_path}")
        self._folder_path = folder_path
        self._module_name = module_name

    def get_mgmt_plane_modules(self, plane):
        names = self._module_name.split('/')
        if not PlaneEnum.is_valid_swagger_module(plane=plane, module_name=names[0]):
            raise InvalidAPIUsage(f"{names[0]} is not a valid mgmt plane module")

        if (os.path.isdir(os.path.join(self._folder_path, 'resource-manager')) or
                TypeSpecHelper.find_mgmt_plane_entry_files(self._folder_path)):
            module = None
            for name in names:
                module = MgmtPlaneModule(plane=plane, name=name, folder_path=None, parent=module)
            module.folder_path = self._folder_path
            assert module is not None
            return [module]

        raise ResourceNotFind(
            f"Cannot find manage plane module '{self._module_name}'",
            payload=f"{self._folder_path}/resource-manager is not exist"
        )

    def get_mgmt_plane_module(self, *names, plane):
        if not names:
            return None
        name = names[0]
        if not PlaneEnum.is_valid_swagger_module(plane=plane, module_name=name):
            return None

        module_str = '/'.join([plane, *names])
        module = None
        for m in self.get_mgmt_plane_modules(plane):
            if str(m) == module_str:
                module = m
                break
        return module

    def get_data_plane_modules(self, plane):
        names = self._module_name.split('/')
        if not PlaneEnum.is_valid_swagger_module(plane=plane, module_name=names[0]):
            raise InvalidAPIUsage(f"{names[0]} is not a supported data plane module.")

        if (os.path.isdir(os.path.join(self._folder_path, 'data-plane')) or
                TypeSpecHelper.find_data_plane_entry_files(self._folder_path)):
            module = None
            for name in names:
                module = DataPlaneModule(plane=plane, name=name, folder_path=None, parent=module)
            module.folder_path = self._folder_path
            assert module is not None
            return [module]

        raise ResourceNotFind(
            f"Cannot find data plane module '{self._module_name}'",
            payload=f"{self._folder_path}/data-plane is not exist"
        )

    def get_data_plane_module(self, *names, plane):
        if not names:
            return None
        name = names[0]
        if not PlaneEnum.is_valid_swagger_module(plane=plane, module_name=name):
            return None

        module_str = '/'.join([plane, *names])
        module = None
        for m in self.get_data_plane_modules(plane):
            if str(m) == module_str:
                module = m
                break
        return module
