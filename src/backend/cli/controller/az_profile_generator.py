import os
import shutil
from cli.templates import get_templates
from command.model.configuration import CMDCommand
from utils.case import to_snack_case
from .az_command_generator import AzCommandGenerator


class AzProfileGenerator:
    """Used to generate atomic layer command group"""

    def __init__(self, aaz_folder, profile):
        self.aaz_folder = aaz_folder
        self.profile = profile
        self.profile_folder_name = profile.name.lower().replace('-', '_')
        self._removed_folders = set()
        self._removed_files = set()
        self._modified_files = {}

    def generate(self):
        # check aaz/__init__.py
        file_name = '__init__.py'
        if not self._exist_file(file_name):
            tmpl = get_templates()['aaz'][file_name]
            data = tmpl.render()
            self._update_file(file_name, data=data)

        if not self.profile.command_groups:
            # remove the whole profile
            self._delete_folder(self.profile_folder_name)
        else:
            # check aaz/{profile}/__init__.py
            file_name = '__init__.py'
            if not self._exist_file(self.profile_folder_name, file_name):
                tmpl = get_templates()['aaz']['profile'][file_name]
                data = tmpl.render()
                self._update_file(self.profile_folder_name, file_name, data=data)

            remain_folders, _ = self._list_package(self.profile_folder_name)
            for command_group in self.profile.command_groups.values():
                assert len(command_group.names) == 1, f"Invalid command group name: {command_group.names}"
                self._generate_by_command_group(
                    profile_folder_name=self.profile_folder_name,
                    command_group=command_group
                )
                if command_group.names[-1] in remain_folders:
                    remain_folders.remove(command_group.names[-1])
            for name in remain_folders:
                self._delete_folder(self.profile_folder_name, name)

        return sorted(self._removed_folders), sorted(self._removed_files), self._modified_files

    def save(self):
        for folder in self._removed_folders:
            shutil.rmtree(folder, ignore_errors=True)
        for file in self._removed_files:
            os.remove(file)
        for path, data in self._modified_files.items():
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w') as f:
                f.write(data)
        self._removed_folders = set()
        self._removed_files = set()
        self._modified_files = {}

    def _generate_by_command_group(self, profile_folder_name, command_group):
        assert command_group.command_groups or command_group.commands

        cur_folders, cur_files = self._list_package(profile_folder_name, *command_group.names)

        folders = set()
        if command_group.command_groups:
            for sub_group in command_group.command_groups.values():
                assert sub_group.names[:-1] == command_group.names, f"Invalid command group name: {sub_group.names}"
                self._generate_by_command_group(profile_folder_name=profile_folder_name, command_group=sub_group)
                folders.add(sub_group.names[-1])

        # delete other folders
        del_folders = cur_folders.difference(folders)
        for name in del_folders:
            self._delete_folder(profile_folder_name, *command_group.names, name)

        files = set()
        if command_group.commands:
            for command in command_group.commands.values():
                assert command.names[:-1] == command_group.names, f"Invalid command name: {command.names}"
                cmd_file_name = self._command_file_name(command.names[-1])
                if cmd_file_name in cur_files:
                    if command.cfg:
                        # configuration attached, that means to update command file
                        self._generate_by_command(profile_folder_name, command)
                else:
                    assert command.cfg is not None
                    self._generate_by_command(profile_folder_name, command)
                files.add(cmd_file_name)

        # update __cmd_group.py file
        file_name = '__cmd_group.py'
        tmpl = get_templates()['aaz']['group'][file_name]
        data = tmpl.render(
            node=command_group
        )
        self._update_file(profile_folder_name, *command_group.names, file_name, data=data)
        files.add(file_name)

        # update __init__.py file
        file_name = '__init__.py'
        tmpl = get_templates()['aaz']['group'][file_name]
        data = tmpl.render(
            file_names=sorted(files)
        )
        self._update_file(profile_folder_name, *command_group.names, file_name, data=data)
        files.add(file_name)

        # delete other files
        del_files = cur_files.difference(files)
        for name in del_files:
            self._delete_file(profile_folder_name, *command_group.names, name)

    def _generate_by_command(self, profile_folder_name, command):
        assert isinstance(command.cfg, CMDCommand)
        file_name = self._command_file_name(command.names[-1])
        tmpl = get_templates()['aaz']['command']['_cmd.py']
        data = tmpl.render(
            leaf=AzCommandGenerator(command)
        )
        self._update_file(profile_folder_name, *command.names[:-1], file_name, data=data)

    # folder operations
    def _get_path(self, *names):
        return os.path.join(self.aaz_folder, *names)

    def _delete_folder(self, *names):
        path = self._get_path(*names)
        if os.path.exists(path):
            assert os.path.isdir(path), f'Invalid folder path {path}'
            self._removed_folders.add(path)

    def _delete_file(self, *names):
        path = self._get_path(*names)
        if os.path.exists(path):
            assert os.path.isfile(path), f'Invalid file path {path}'
            self._removed_files.add(path)

    def _update_file(self, *names, data):
        path = self._get_path(*names)
        if os.path.exists(path):
            assert os.path.isfile(path), f'Invalid file path {path}'
        self._modified_files[path] = data

    def _exist_file(self, *names):
        path = self._get_path(*names)
        if os.path.exists(path):
            assert os.path.isfile(path), f'Invalid file path {path}'
            return True
        return False

    def _list_package(self, *names):
        path = self._get_path(*names)
        folder_names = []
        file_names = []
        if os.path.exists(path):
            assert os.path.isdir(path), f'Invalid folder path {path}'
            for name in os.listdir(path):
                sub_path = os.path.join(path, name)
                if os.path.isfile(sub_path):
                    if name.endswith('.py'):
                        file_names.append(name)
                elif os.path.isdir(sub_path):
                    init_file = os.path.join(sub_path, '__init__.py')
                    if os.path.exists(init_file) and os.path.isfile(init_file):
                        folder_names.append(name)
        return set(folder_names), set(file_names)

    @staticmethod
    def _command_file_name(name):
        return f"_{to_snack_case(name)}.py"
