import os
import shutil
from cli.templates import get_templates
from command.model.configuration import CMDCommand
from utils.case import to_snake_case
from .az_command_generator import AzCommandGenerator
from .az_client_generator import AzClientsGenerator
from utils import exceptions


class AzProfileGenerator:
    """Used to generate atomic layer command group"""

    def __init__(self, aaz_folder, profile):
        self.aaz_folder = aaz_folder
        self.profile = profile
        self.profile_folder_name = profile.profile_folder_name
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
            # remove the whole aaz/{profile}
            self._delete_folder(self.profile_folder_name)
        else:
            # generate clients
            # aaz/{profile}/_clients.py
            has_clients = self._generate_by_clients(self.profile_folder_name, self.profile.clients)
            # aaz/{profile}/__init__.py
            file_name = '__init__.py'
            tmpl = get_templates()['aaz']['profile'][file_name]
            data = tmpl.render(has_clients=has_clients)
            self._update_file(self.profile_folder_name, file_name, data=data)

            remain_folders, _ = self._list_package(self.profile_folder_name)
            for command_group in self.profile.command_groups.values():
                assert len(command_group.names) == 1, f"Invalid command group name: {command_group.names}"
                command_group_folder_name = command_group.names[-1].replace('-', '_')
                self._generate_by_command_group(
                    profile_folder_name=self.profile_folder_name,
                    command_group=command_group
                )
                if command_group_folder_name in remain_folders:
                    remain_folders.remove(command_group_folder_name)
            for name in remain_folders:
                self._delete_folder(self.profile_folder_name, name)

        return sorted(self._removed_folders), sorted(self._removed_files), self._modified_files

    def save(self):
        for folder in self._removed_folders:
            shutil.rmtree(folder, ignore_errors=True)
        for file in self._removed_files:
            try:
                os.remove(file)
            except FileNotFoundError:
                pass
        for path, data in self._modified_files.items():
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w', encoding="utf-8") as f:
                f.write(data)
        self._removed_folders = set()
        self._removed_files = set()
        self._modified_files = {}

    def _generate_by_command_group(self, profile_folder_name, command_group):
        assert command_group.command_groups or command_group.commands

        command_group_folder_names = self._command_group_folder_names(*command_group.names)
        cur_folders, cur_files = self._list_package(profile_folder_name, *command_group_folder_names)

        folders = set()
        if command_group.command_groups:
            for sub_group in command_group.command_groups.values():
                assert sub_group.names[:-1] == command_group.names, f"Invalid command group name: {sub_group.names}"
                self._generate_by_command_group(profile_folder_name=profile_folder_name, command_group=sub_group)
                sub_group_folder_name = sub_group.names[-1].replace('-', '_')
                folders.add(sub_group_folder_name)

        # delete other folders
        del_folders = cur_folders.difference(folders)
        for name in del_folders:
            self._delete_folder(profile_folder_name, *command_group_folder_names, name)

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
            if command_group.wait_command:
                command = command_group.wait_command
                cmd_file_name = self._command_file_name(command.names[-1])
                if command.cfg:
                    # configuration attached, that means to update command file
                    self._generate_by_command(profile_folder_name, command, is_wait=True)
                files.add(cmd_file_name)

        # update __cmd_group.py file
        file_name = '__cmd_group.py'
        tmpl = get_templates()['aaz']['group'][file_name]
        data = tmpl.render(
            node=command_group
        )
        self._update_file(profile_folder_name, *command_group_folder_names, file_name, data=data)
        files.add(file_name)

        # update __init__.py file
        file_name = '__init__.py'
        tmpl = get_templates()['aaz']['group'][file_name]
        data = tmpl.render(
            file_names=sorted(files)
        )
        self._update_file(profile_folder_name, *command_group_folder_names, file_name, data=data)
        files.add(file_name)

        # delete other files
        del_files = cur_files.difference(files)
        for name in del_files:
            self._delete_file(profile_folder_name, *command_group_folder_names, name)

    def _generate_by_command(self, profile_folder_name, command, is_wait=False):
        assert isinstance(command.cfg, CMDCommand)
        file_name = self._command_file_name(command.names[-1])
        tmpl = get_templates()['aaz']['command']['_cmd.py']
        client = self.profile.get_client(command)
        assert client is not None
        try:
            data = tmpl.render(
                leaf=AzCommandGenerator(command, client, is_wait=is_wait)
            )
        except exceptions.InvalidAPIUsage as err:
            err.message = f"CommandGenerationError: {' '.join(command.names)}: {err.message}"
            raise err
        self._update_file(
            profile_folder_name, *self._command_group_folder_names(*command.names[:-1]), file_name, data=data)

    def _generate_by_clients(self, profile_folder_name, clients):
        generator = AzClientsGenerator(clients)
        if generator.is_empty():
            self._delete_file(profile_folder_name, '_clients.py')
            return False
        tmpl = get_templates()['aaz']['profile']['_clients.py']
        try:
            data = tmpl.render(
                leaf=generator
            )
        except exceptions.InvalidAPIUsage as err:
            err.message = f"AzClientsGenerator: {err.message}"
            raise err
        self._update_file(profile_folder_name, '_clients.py', data=data)
        return True

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
        return f"_{to_snake_case(name)}.py"

    @staticmethod
    def _command_group_folder_names(*names):
        return [name.replace('-', '_') for name in names]
