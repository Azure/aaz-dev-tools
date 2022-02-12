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

    @staticmethod
    def pkg_name(mod_name):
        return mod_name.replace('-', '_').lower()

    def get_mod_path(self, mod_name):
        return os.path.join(self.folder, self.pkg_name(mod_name))

    def get_aaz_path(self, mod_name):
        return os.path.join(self.get_mod_path(mod_name), 'aaz')

    def list_modules(self):
        modules = []
        for _, pkg_name, _ in pkgutil.iter_modules(path=[self.folder]):
            modules.append({
                "name": pkg_name.replace('_', '-'),
                "folder": os.path.join(self.folder, pkg_name)
            })

        return sorted(modules, key=lambda a: a['name'])

    def create_new_mod(self, mod_name):
        mod_path = self.get_mod_path(mod_name)
        templates = get_templates()['main']
        new_files = {}

        # render __init__.py
        file_path = os.path.join(mod_path, '__init__.py')
        if os.path.exists(file_path):
            raise exceptions.ResourceConflict(f"File already exist: '{file_path}'")
        tmpl = templates['__init__.py']
        new_files[file_path] = tmpl.render(
            mod_name=mod_name
        )

        # render _help.py
        file_path = os.path.join(mod_path, '_help.py')
        if os.path.exists(file_path):
            raise exceptions.ResourceConflict(f"File already exist: '{file_path}'")
        tmpl = templates['_help.py']
        new_files[file_path] = tmpl.render()

        # render _params.py
        file_path = os.path.join(mod_path, '_params.py')
        if os.path.exists(file_path):
            raise exceptions.ResourceConflict(f"File already exist: '{file_path}'")
        tmpl = templates['_params.py']
        new_files[file_path] = tmpl.render()

        # render commands.py
        file_path = os.path.join(mod_path, 'commands.py')
        if os.path.exists(file_path):
            raise exceptions.ResourceConflict(f"File already exist: '{file_path}'")
        tmpl = templates['commands.py']
        new_files[file_path] = tmpl.render()

        # render custom.py
        file_path = os.path.join(mod_path, 'custom.py')
        if os.path.exists(file_path):
            raise exceptions.ResourceConflict(f"File already exist: '{file_path}'")
        tmpl = templates['custom.py']
        new_files[file_path] = tmpl.render()

        # test_folder
        t_path = os.path.join(mod_path, 'tests')
        t_templates = templates['tests']

        # render __init__.py
        file_path = os.path.join(t_path, '__init__.py')
        if os.path.exists(file_path):
            raise exceptions.ResourceConflict(f"File already exist: '{file_path}'")
        tmpl = t_templates['__init__.py']
        new_files[file_path] = tmpl.render()

        profile = Config.CLI_DEFAULT_PROFILE
        tp_path = os.path.join(t_path, profile)
        tp_templates = t_templates['profile']

        # render __init__.py
        file_path = os.path.join(tp_path, '__init__.py')
        if os.path.exists(file_path):
            raise exceptions.ResourceConflict(f"File already exist: '{file_path}'")
        tmpl = tp_templates['__init__.py']
        new_files[file_path] = tmpl.render()

        # render test_*.py
        file_path = os.path.join(tp_path, f'test_{self.pkg_name(mod_name)}.py')
        if os.path.exists(file_path):
            raise exceptions.ResourceConflict(f"File already exist: '{file_path}'")
        tmpl = tp_templates['test_.py']
        new_files[file_path] = tmpl.render(name=mod_name)

        # written files
        for path, data in new_files.items():
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w') as f:
                f.write(data)

    def setup_aaz_folder(self, mod_name):
        pass

    def load_module(self, mod_name):
        pass
