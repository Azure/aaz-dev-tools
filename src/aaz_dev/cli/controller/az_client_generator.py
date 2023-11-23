from utils import exceptions
import logging

from cli.model.atomic import CLIAtomicClient
from command.model.configuration import CMDClientEndpointsByHttpOperation, CMDClientEndpointsByTemplate, CMDJsonSubresourceSelector
from .az_command_ctx import AzCommandCtx
from .az_command_generator import AzCommandGenerator
from .az_arg_group_generator import AzArgGroupGenerator
from .az_selector_generator import AzJsonSelectorGenerator
from .az_operation_generator import AzHttpOperationGenerator
from utils.plane import PlaneEnum
from utils.case import to_camel_case

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
        self.cmd_ctx = AzCommandCtx()
        if self._client.cfg.arg_group:
            # Register client arguments in _cmd_ctx
            AzArgGroupGenerator(AzCommandGenerator.ARGS_SCHEMA_NAME, self.cmd_ctx, self._client.cfg.arg_group)
        if isinstance(self._client.cfg.endpoints, CMDClientEndpointsByTemplate):
            self.endpoints = AzClientEndpointsByTemplateGenerator(self._client.cfg.endpoints)
        elif isinstance(self._client.cfg.endpoints, CMDClientEndpointsByHttpOperation):
            self.endpoints = AzClientEndpointsByHttpOperationGenerator(self._client.cfg.endpoints, self.cmd_ctx)
        else:
            raise NotImplementedError()

    @property
    def registered_name(self):
        return self._client.registered_name

    @property
    def cls_name(self):
        return self._client.cls_name

    @property
    def aad_scopes(self):
        return self._client.cfg.auth.aad.scopes

    @property
    def helper_cls_name(self):
        return f'_{self.cls_name}Helper'

    def get_arg_clses(self):
        return sorted(self.cmd_ctx.arg_clses.values(), key=lambda a: a.name)

    def get_update_clses(self):
        return sorted(self.cmd_ctx.update_clses.values(), key=lambda s: s.name)

    def get_response_clses(self):
        return sorted(self.cmd_ctx.response_clses.values(), key=lambda s: s.name)


class AzClientEndpointsByTemplateGenerator:

    def __init__(self, endpoints):
        assert isinstance(endpoints, CMDClientEndpointsByTemplate)
        self._endpoints = endpoints

    @property
    def type(self):
        return self._endpoints.type

    def iter_hosts(self):
        for template in self._endpoints.templates:
            yield template.cloud, template.template


class AzClientEndpointsByHttpOperationGenerator:

    def __init__(self, endpoints, cmd_ctx):
        assert isinstance(endpoints, CMDClientEndpointsByHttpOperation)
        self._endpoints = endpoints
        self._cmd_ctx = cmd_ctx
        if isinstance(endpoints.selector, CMDJsonSubresourceSelector):
            self.selector = AzJsonSelectorGenerator(self._cmd_ctx, endpoints.selector)
        else:
            raise NotImplementedError()
        op_cls_name = to_camel_case(endpoints.operation.operation_id)
        self.operation = AzHttpOperationGenerator(
            op_cls_name,
            self._cmd_ctx,
            endpoints.operation,
            client_endpoints=None,
        )
        # Only arm endpoints is allowed
        assert endpoints.resource.plane == PlaneEnum.Mgmt
        self.client_name = PlaneEnum.http_client(endpoints.resource.plane)

    @property
    def type(self):
        return self._endpoints.type

