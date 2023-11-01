from utils import exceptions
import logging
from cli.model.atomic import CLIAtomicCommand, CLIAtomicClient

logger = logging.getLogger('backend')


class AzClientsGenerator:

    def __init__(self, clients: [CLIAtomicClient]):
        # only clients with cfg will be generated.
        self._clients = sorted([client for client in clients if client.cfg], key=lambda c: c.registered_name)

    def iter_clients(self):
        for client in self._clients:
            yield AzClientGenerator(client)

    def is_empty(self):
        return len(self._clients) == 0


class AzClientGenerator:

    def __init__(self, client):
        self._client = client

    @property
    def registered_name(self):
        return self._client.registered_name

    def iter_hosts(self):
        for template in self._client.cfg.endpoints.templates:
            yield template.cloud, template.template

    @property
    def aad_scopes(self):
        return self._client.cfg.auth.aad.scopes
