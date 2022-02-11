from utils.config import Config
import os
from utils import exceptions
import glob

_folder = None
_folder_is_module = None


class AzExtensionManager:

    def __init__(self):
        global _folder
        global _folder_is_module

        cli_ext_folder = Config.CLI_EXTENSION_PATH
        if not os.path.exists(cli_ext_folder) or not os.path.isdir(cli_ext_folder):
            raise ValueError(f"Invalid Cli Extension Repo folder: '{cli_ext_folder}'")

        if not _folder:
            module_paths = []
            for path, _, _ in os.walk(cli_ext_folder):
                if 'azext_' in path:
                    continue
                ext_paths = [path for path in glob.glob(os.path.join(path, 'azext_*')) if os.path.isdir(path)]
                if ext_paths and os.path.exists(os.path.join(path, 'setup.py')):
                    module_paths.append(path)
            module_paths = sorted(module_paths)
            if not module_paths:
                _folder = os.path.join(cli_ext_folder, 'src')
                _folder_is_module = False
            elif module_paths[0] == cli_ext_folder:
                _folder = cli_ext_folder
                _folder_is_module = True
            else:
                folders = list(set([os.path.dirname(path) for path in module_paths]))
                if len(folders) > 1:
                    raise ValueError(f"Invalid Cli Extension Repo: '{cli_ext_folder}', Modules in multi folders: {folders}")
                _folder = folders[0]
                assert _folder.startswith(cli_ext_folder) and len(_folder) > len(cli_ext_folder)
                _folder_is_module = False

        self.folder = _folder
        self.folder_is_module = _folder_is_module

    def get_mod_path(self, mod_name):
        if self.folder_is_module:
            name = self._get_module_name_by_path(self.folder)
            if name == mod_name:
                return self.folder
            else:
                raise exceptions.ResourceConflict(f"Invalid Module name, only support '{name}'")
        else:
            return os.path.join(self.folder, mod_name)

    @staticmethod
    def _generate_mod_ext_name(mod_name):
        return 'azext_' + mod_name.replace('-', '_').lower()

    @staticmethod
    def _get_module_name_by_path(path):
        return os.path.split(path)[-1]

    def get_mod_ext_path(self, mod_name):
        mod_path = self.get_mod_path(mod_name)
        ext_paths = [path for path in glob.glob(os.path.join(mod_path, 'azext_*')) if os.path.isdir(path)]
        if not ext_paths:
            return os.path.join(mod_path, self._generate_mod_ext_name(mod_name))
        else:
            if len(ext_paths) > 1:
                raise exceptions.ResourceConflict(f"Find multi folders start with 'azext_' in module path '{mod_path}'")
            return ext_paths[0]

    def get_aaz_path(self, mod_name):
        return os.path.join(self.get_mod_ext_path(mod_name), 'aaz')

    def list_modules(self):
        modules = []
        if self.folder_is_module:
            modules.append({
                "name": self._get_module_name_by_path(self.folder),
                "folder": self.folder
            })
        else:
            for setup_path in glob.glob(os.path.join(self.folder, '*', 'setup.py')):
                module_folder = os.path.dirname(setup_path)
                modules.append({
                    "name": self._get_module_name_by_path(module_folder),
                    "folder": module_folder
                })
        return modules

    def create_new_mod(self, mod_name):
        if self.folder_is_module:
            raise exceptions.ResourceConflict(
                f"Cannot create a new module in cli extension repo('{Config.CLI_EXTENSION_PATH}'), "
                f"because the repo is an extension module"
            )
        mod_path = self.get_mod_path(mod_name)
        if os.path.exists(os.path.join(mod_path, '__init__.py')):
            raise exceptions.ResourceConflict(f"Module already exist in path: '{mod_path}'")

        raise NotImplementedError()

    def setup_aaz_folder(self, mod_name):
        pass

    def load_module(self, mod_name):
        pass

