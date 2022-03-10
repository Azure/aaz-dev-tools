import os
import pkgutil
import glob

from cli.model.atomic import CLIAtomicProfile, CLIModule, CLIAtomicCommandGroup, CLIAtomicCommandGroupRegisterInfo, \
    CLIAtomicCommand, CLIAtomicCommandRegisterInfo, CLISpecsResource, CLICommandGroupHelp, CLICommandHelp, CLICommandExample
from cli.templates import get_templates
from command.controller.specs_manager import AAZSpecsManager
from cli.controller.az_profile_generator import AzProfileGenerator
from utils import exceptions
from utils.config import Config
from utils.stage import AAZStageEnum
import re
import json
import logging

logger = logging.getLogger('backend')


class AzModuleManager:

    _command_group_pattern = re.compile(r'^class\s+(.*)\(.*AAZCommandGroup.*\)\s*:\s*$')
    _command_pattern = re.compile(r'^class\s+(.*)\(.*AAZCommand.*\)\s*:\s*$')
    _is_preview_param = re.compile(r'\s*is_preview\s*=\s*True\s*')
    _is_experimental_param = re.compile(r'\s*is_experimental\s*=\s*True\s*')
    _def_pattern = re.compile(r'^\s*def\s+')
    _aaz_info_pattern = re.compile(r'^\s*_aaz_info\s*=\s*({.*)$')

    def __init__(self):
        self._aaz_spec_manager = AAZSpecsManager()

    @staticmethod
    def pkg_name(mod_name):
        return mod_name.replace('-', '_').lower()

    def get_mod_path(self, mod_name):
        raise NotImplementedError()

    def get_aaz_path(self, mod_name):
        raise NotImplementedError()

    def load_module(self, mod_name):
        module = CLIModule()
        module.name = mod_name
        module.folder = self.get_mod_path(mod_name)

        module.profiles = {}
        for profile_name in Config.CLI_PROFILES:
            module.profiles[profile_name] = self._load_profile(profile_name, self.get_aaz_path(mod_name))

        return module

    def update_module(self, mod_name, profiles):
        aaz_folder = self.get_aaz_path(mod_name)
        generators = {}
        for profile_name, profile in profiles.items():
            if profile.command_groups:
                for command_group in profile.command_groups.values():
                    self._load_commands_cfg(command_group)
            generators[profile_name] = AzProfileGenerator(aaz_folder, profile)
        for generator in generators.values():
            generator.generate()
        for generator in generators.values():
            generator.save()
        module = CLIModule()
        module.name = mod_name
        module.folder = self.get_mod_path(mod_name)
        module.profiles = profiles
        return module

    def _load_profile(self, profile_name, aaz_path):
        profile = CLIAtomicProfile()
        profile.name = profile_name
        profile_path = os.path.join(aaz_path, profile_name)
        if not os.path.exists(profile_path):
            return profile

        profile.command_groups = self._load_command_groups(path=profile_path)

        return profile

    def _load_command_groups(self, *names, path):
        command_groups = {}
        assert os.path.isdir(path), f'Invalid folder path {path}'
        for name in os.listdir(path):
            sub_path = os.path.join(path, name)
            if os.path.isdir(sub_path):
                command_group = self._load_command_group(*names, name, path=sub_path)
                if command_group:
                    command_groups[name] = command_group
        if not command_groups:
            return None
        return command_groups

    def _load_commands(self, *names, path):
        commands = {}
        assert os.path.isdir(path), f'Invalid folder path {path}'
        for name in os.listdir(path):
            sub_path = os.path.join(path, name)
            if os.path.isfile(sub_path) and name.endswith('.py') and not name.startswith('__') and name.startswith('_'):
                name = name[1:-3].replace('_', '-')
                command = self._load_command(*names, name, path=sub_path)
                if command:
                    commands[name] = command
        if not commands:
            return None
        return commands

    def _load_command_group(self, *names, path):
        assert os.path.isdir(path), f'Invalid folder path {path}'
        init_file = os.path.join(path, '__init__.py')
        if not os.path.exists(init_file) or not os.path.isfile(init_file):
            return None
        cmd_group_file = os.path.join(path, '__cmd_group.py')
        if not os.path.exists(cmd_group_file) or not os.path.isfile(cmd_group_file):
            return None

        register_info_lines = None
        find_command_group = False
        with open(cmd_group_file, 'r') as f:
            while f.readable():
                line = f.readline()
                if line.startswith('@register_command_group('):
                    register_info_lines = []
                if register_info_lines is not None:
                    register_info_lines.append(line)
                if self._command_group_pattern.match(line):
                    find_command_group = True
                    break
        if not find_command_group:
            return None

        # load from aaz
        command_group = self.build_command_group_from_aaz(*names)
        if not command_group:
            logger.error(f"CommandGroup miss in aaz repo: '{' '.join(names)}'")
            return None

        if register_info_lines:
            command_group.register_info = CLIAtomicCommandGroupRegisterInfo()
            for line in register_info_lines:
                if self._is_preview_param.findall(line):
                    command_group.register_info.stage = AAZStageEnum.Preview
                if self._is_experimental_param.findall(line):
                    command_group.register_info.stage = AAZStageEnum.Experimental

        command_group.command_groups = self._load_command_groups(*names, path=path)
        command_group.commands = self._load_commands(*names, path=path)
        return command_group

    def build_command_group_from_aaz(self, *names):
        aaz_cg = self._aaz_spec_manager.find_command_group(*names)
        if not aaz_cg:
            return None
        command_group = CLIAtomicCommandGroup()
        command_group.names = [*names]
        command_group.help = CLICommandGroupHelp()
        command_group.help.short = aaz_cg.help.shrot
        if aaz_cg.help.lines:
            command_group.help.long = '\n'.join(aaz_cg.help.lines)
        return command_group

    def _load_command(self, *names, path):
        assert os.path.isfile(path), f'Invalid file path {path}'

        register_info_lines = None
        aaz_info_lines = None
        find_command = False
        with open(path, 'r') as f:
            while f.readable():
                line = f.readline()
                if line.startswith('@register_command('):
                    register_info_lines = []
                if register_info_lines is not None:
                    register_info_lines.append(line)
                if self._command_pattern.match(line):
                    find_command = True
                    break
            if not find_command:
                return None

            while f.readable():
                line = f.readline()
                if self._def_pattern.findall(line):
                    break
                match = self._aaz_info_pattern.match(line)
                if match:
                    aaz_info_lines = match[1]
                    while f.readable():
                        line = f.readline()
                        line = line.strip()
                        aaz_info_lines += ' ' + line
                        if line.endswith('}'):
                            break
                    break

        if not find_command:
            return None

        if not aaz_info_lines:
            logger.error(f"Command info miss in code: '{' '.join(names)}'")
            return None

        try:
            data = json.loads(aaz_info_lines)
            version_name = data['version']
        except Exception as err:
            logger.error(f"Command info invalid in code: '{' '.join(names)}': {err}")
            return None

        command = self.build_command_from_aaz(*names, version_name=version_name)
        if not command:
            logger.error(f"Command miss in aaz repo: '{' '.join(names)}'")
            return None

        if register_info_lines:
            command.register_info = CLIAtomicCommandRegisterInfo()
            for line in register_info_lines:
                if self._is_preview_param.findall(line):
                    command.register_info.stage = AAZStageEnum.Preview
                if self._is_experimental_param.findall(line):
                    command.register_info.stage = AAZStageEnum.Experimental
        return command

    def build_command_from_aaz(self, *names, version_name):
        aaz_cmd = self._aaz_spec_manager.find_command(*names)
        if not aaz_cmd:
            return None
        version = None
        for v in (aaz_cmd.versions or []):
            if v.name == version_name:
                version = v
                break
        if not version:
            return None

        command = CLIAtomicCommand()
        command.names = [*names]
        command.help = CLICommandHelp()
        command.help.short = aaz_cmd.help.short
        if aaz_cmd.help.lines:
            command.help.long = '\n'.join(aaz_cmd.help.lines)

        if version.examples:
            command.help.examples = [CLICommandExample(e.to_primitive()) for e in version.examples]

        command.version = version.name
        command.stage = version.stage
        command.resources = [CLISpecsResource(r.to_primitive()) for r in version.resources]

        return command

    def _load_commands_cfg(self, command_group):
        if command_group.commands:
            for command in command_group.commands.values():
                self._load_command_cfg(command)
        if command_group.command_groups:
            for sub_group in command_group.command_groups.values():
                self._load_commands_cfg(sub_group)

    def _load_command_cfg(self, command):
        aaz_cmd = self._aaz_spec_manager.find_command(*command.names)
        if not aaz_cmd:
            raise exceptions.InvalidAPIUsage(f"Command miss in aaz repo: '{' '.join(command.names)}'")
        version = None
        for v in (aaz_cmd.versions or []):
            if v.name == command.version:
                version = v
                break
        if not version:
            raise exceptions.InvalidAPIUsage(f"Command Version miss in aaz repo: '{' '.join(command.names)}' '{command.version}'")
        cfg_reader = self._aaz_spec_manager.load_resource_cfg_reader_by_command_with_version(aaz_cmd, version=version)
        cmd_cfg = cfg_reader.find_command(*command.names)
        assert cmd_cfg is not None, f"command configuration miss: '{' '.join(command.names)}'"
        command.cfg = cmd_cfg


class AzMainManager(AzModuleManager):

    @classmethod
    def _find_module_folder(cls):
        cli_folder = Config.CLI_PATH
        if not os.path.exists(cli_folder) or not os.path.isdir(cli_folder):
            raise ValueError(f"Invalid Cli Main Repo folder: '{cli_folder}'")
        module_folder = os.path.join(cli_folder, "src", "azure-cli", "azure", "cli", "command_modules")
        if not os.path.exists(module_folder):
            raise ValueError(f"Invalid Cli Main Repo folder: cannot find modules in: '{module_folder}'")
        return module_folder

    def __init__(self):
        super().__init__()
        module_folder = self._find_module_folder()
        self.folder = module_folder

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

        module = CLIModule()
        module.name = mod_name
        module.folder = self.get_mod_path(mod_name)

        module.profiles = {}
        for profile_name in Config.CLI_PROFILES:
            module.profiles[profile_name] = self._load_profile(profile_name, self.get_aaz_path(mod_name))

        return module

    def setup_aaz_folder(self, mod_name):
        pass


class AzExtensionManager(AzModuleManager):

    _folder = None
    _folder_is_module = None

    @classmethod
    def _find_module_folder(cls):
        cli_ext_folder = Config.CLI_EXTENSION_PATH
        if not os.path.exists(cli_ext_folder) or not os.path.isdir(cli_ext_folder):
            raise ValueError(f"Invalid Cli Extension Repo folder: '{cli_ext_folder}'")

        if not cls._folder:
            module_paths = []
            for path, _, _ in os.walk(cli_ext_folder):
                if 'azext_' in path:
                    continue
                ext_paths = [path for path in glob.glob(os.path.join(path, 'azext_*')) if os.path.isdir(path)]
                if ext_paths and os.path.exists(os.path.join(path, 'setup.py')):
                    module_paths.append(path)
            module_paths = sorted(module_paths)
            if not module_paths:
                cls._folder = os.path.join(cli_ext_folder, 'src')
                cls._folder_is_module = False
            elif module_paths[0] == cli_ext_folder:
                cls._folder = cli_ext_folder
                cls._folder_is_module = True
            else:
                folders = list(set([os.path.dirname(path) for path in module_paths]))
                if len(folders) > 1:
                    raise ValueError(
                        f"Invalid Cli Extension Repo: '{cli_ext_folder}', Modules in multi folders: {folders}")
                cls._folder = folders[0]
                assert cls._folder.startswith(cli_ext_folder) and len(cls._folder) > len(cli_ext_folder)
                cls._folder_is_module = False
        return cls._folder, cls._folder_is_module

    def __init__(self):
        super().__init__()
        self.folder, self.folder_is_module = self._find_module_folder()

    def get_mod_path(self, mod_name):
        if self.folder_is_module:
            name = self._get_module_name_by_path(self.folder)
            if name == mod_name:
                return self.folder
            else:
                raise exceptions.ResourceConflict(f"Invalid Module name, only support '{name}'")
        else:
            return os.path.join(self.folder, mod_name)

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
        from packaging import version
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
