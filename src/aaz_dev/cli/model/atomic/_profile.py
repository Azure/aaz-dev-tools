from schematics.models import Model
from schematics.types import ModelType, DictType

from ._command_group import CLIAtomicCommandGroup
from ._client import CLIAtomicClient
from cli.model.common._fields import CLIProfileNameField

from utils.plane import PlaneEnum


class CLIAtomicProfile(Model):
    name = CLIProfileNameField(required=True)
    command_groups = DictType(
        field=ModelType(CLIAtomicCommandGroup),
        serialized_name="commandGroups",
        deserialize_from="commandGroups"
    )
    _clients = DictType(
        field=ModelType(CLIAtomicClient),
        serialized_name="clients",
        deserialize_from="clients",
    )

    class Options:
        serialize_when_none = False

    @property
    def profile_folder_name(self):
        profile_folder_name = self.name.lower().replace('-', '_')
        if profile_folder_name != "latest":
            # for rest profiles such as 2019-03-01-hybrid, the folder name starts with digit,
            # it's not a valid python package name.
            profile_folder_name = "profile_" + profile_folder_name
        return profile_folder_name

    def get_client(self, command):
        if not self._clients:
            return None
        plane = command.resources[0].plane
        name = PlaneEnum.http_client(plane)
        return self._clients.get(f'{plane}/{name}', None)

    def add_client(self, client):
        if not self._clients:
            self._clients = {}
        self._clients[f'{client.plane}/{client.name}'] = client

    @property
    def clients(self):
        return [*self._clients.values()]
