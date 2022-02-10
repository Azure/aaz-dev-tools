from utils.config import Config
import os
import pkgutil
from utils import exceptions
from cli.templates import get_templates


class AzMainManager:

    def __init__(self):
        cli_folder = Config.CLI_PATH
        if not os.path.exists(cli_folder) or not os.path.isdir(cli_folder):
            raise ValueError(f"Invalid Cli Main Repo folder: '{cli_folder}'")
        module_folder = os.path.join(cli_folder, "src", "azure-cli", "azure", "cli", "command_modules")
        if not os.path.exists(module_folder):
            raise ValueError(f"Invalid Cli Main Repo folder: cannot find modules in: '{module_folder}'")

        self.folder = module_folder

    def get_mod_path(self, mod_name):
        return os.path.join(self.folder, mod_name)

    def get_aaz_path(self, mod_name):
        return os.path.join(self.get_mod_path(mod_name), 'aaz')

    def list_modules(self):
        modules = []
        for _, modname, _ in pkgutil.iter_modules(path=[self.folder]):
            modules.append({
                "name": modname,
                "folder": os.path.join(self.folder, modname)
            })

        return sorted(modules, key=lambda a: a['name'])

    def create_new_mod(self, mod_name):
        mod_path = self.get_mod_path(mod_name)
        if os.path.exists(os.path.join(mod_path, '__init__.py')):
            raise exceptions.ResourceConflict(f"Module already exist in path: '{mod_path}'")

        raise NotImplementedError()

    def load_module(self, mod_name):
        pass
