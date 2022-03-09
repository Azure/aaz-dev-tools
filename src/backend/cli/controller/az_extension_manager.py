import glob
import json
import os

from cli.model.atomic import CLIAtomicProfile
from cli.templates import get_templates
from packaging import version
from utils import exceptions
from utils.config import Config

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
                    raise ValueError(
                        f"Invalid Cli Extension Repo: '{cli_ext_folder}', Modules in multi folders: {folders}")
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
    def pkg_name(mod_name):
        return mod_name.replace('-', '_').lower()

    def _generate_mod_ext_name(self, mod_name):
        return 'azext_' + self.pkg_name(mod_name)

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

    def create_mod_azext_metadata(self, mod_name):
        ext_path = self.get_mod_ext_path(mod_name)
        metadata_path = os.path.join(ext_path, 'azext_metadata.json')
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            if "azext.minCliCoreVersion" not in metadata or \
                    version.parse(metadata["azext.minCliCoreVersion"]) < Config.MIN_CLI_CORE_VERSION:
                metadata["azext.minCliCoreVersion"] = str(Config.MIN_CLI_CORE_VERSION)
        else:
            metadata = {
                "azext.isExperimental": True,
                "azext.minCliCoreVersion": str(Config.MIN_CLI_CORE_VERSION),
            }
        return metadata

    def create_new_mod(self, mod_name):
        if self.folder_is_module:
            raise exceptions.ResourceConflict(
                f"Cannot create a new module in cli extension repo('{Config.CLI_EXTENSION_PATH}'), "
                f"because the repo is an extension module"
            )
        mod_path = self.get_mod_path(mod_name)
        templates = get_templates()['extension']
        new_files = {}

        # render HISTORY.rst
        file_path = os.path.join(mod_path, 'HISTORY.rst')
        if os.path.exists(file_path):
            raise exceptions.ResourceConflict(f"File already exist: '{file_path}'")
        tmpl = templates['HISTORY.rst']
        new_files[file_path] = tmpl.render()

        # render readme.md
        file_path = os.path.join(mod_path, 'readme.md')
        if os.path.exists(file_path):
            raise exceptions.ResourceConflict(f"File already exist: '{file_path}'")
        tmpl = templates['readme.md']
        new_files[file_path] = tmpl.render(
            mod_name=mod_name
        )

        # render setup.cfg
        file_path = os.path.join(mod_path, 'setup.cfg')
        if os.path.exists(file_path):
            raise exceptions.ResourceConflict(f"File already exist: '{file_path}'")
        tmpl = templates['setup.cfg']
        new_files[file_path] = tmpl.render()

        # render setup.py
        file_path = os.path.join(mod_path, 'setup.py')
        if os.path.exists(file_path):
            raise exceptions.ResourceConflict(f"File already exist: '{file_path}'")
        tmpl = templates['setup.py']
        new_files[file_path] = tmpl.render(
            mod_name=mod_name
        )

        # azext_* folder
        ext_path = self.get_mod_ext_path(mod_name)
        ext_templates = templates['azext_']

        # render __init__.py
        file_path = os.path.join(ext_path, '__init__.py')
        if os.path.exists(file_path):
            raise exceptions.ResourceConflict(f"File already exist: '{file_path}'")
        tmpl = ext_templates['__init__.py']
        new_files[file_path] = tmpl.render(
            mod_name=mod_name
        )

        # render _help.py
        file_path = os.path.join(ext_path, '_help.py')
        if os.path.exists(file_path):
            raise exceptions.ResourceConflict(f"File already exist: '{file_path}'")
        tmpl = ext_templates['_help.py']
        new_files[file_path] = tmpl.render()

        # render _params.py
        file_path = os.path.join(ext_path, '_params.py')
        if os.path.exists(file_path):
            raise exceptions.ResourceConflict(f"File already exist: '{file_path}'")
        tmpl = ext_templates['_params.py']
        new_files[file_path] = tmpl.render()

        # render commands.py
        file_path = os.path.join(ext_path, 'commands.py')
        if os.path.exists(file_path):
            raise exceptions.ResourceConflict(f"File already exist: '{file_path}'")
        tmpl = ext_templates['commands.py']
        new_files[file_path] = tmpl.render()

        # render custom.py
        file_path = os.path.join(ext_path, 'custom.py')
        if os.path.exists(file_path):
            raise exceptions.ResourceConflict(f"File already exist: '{file_path}'")
        tmpl = ext_templates['custom.py']
        new_files[file_path] = tmpl.render()

        # azext_metadata.json
        file_path = os.path.join(ext_path, 'azext_metadata.json')
        if os.path.exists(file_path):
            raise exceptions.ResourceConflict(f"File already exist: '{file_path}'")
        ext_metadata = self.create_mod_azext_metadata(mod_name)
        new_files[file_path] = json.dumps(ext_metadata, indent=4, sort_keys=True)

        # test_folder
        t_path = os.path.join(ext_path, 'tests')
        t_templates = ext_templates['tests']

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

        profile = CLIAtomicProfile()
        profile.name = Config.CLI_DEFAULT_PROFILE

        return {
            "name": mod_name,
            "folder": mod_path,
            "profiles": [
                profile.to_primitive()
            ],
        }

    def setup_aaz_folder(self, mod_name):
        pass

    def load_module(self, mod_name):
        pass
