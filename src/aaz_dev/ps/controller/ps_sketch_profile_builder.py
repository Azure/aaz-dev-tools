import logging
import os

from utils.exceptions import ResourceNotFind
from ps.model.sketch import PSSketchProfile, PSSketchResourceProvider, PSSketchResource
from swagger.controller.specs_manager import SwaggerSpecsManager
from command.controller.specs_manager import AAZSpecsManager
from cli.model.view import CLIViewProfile
logger = logging.getLogger('backend')


class PSSketchProfileBuilder:

    def __init__(self, aaz_specs_manager: AAZSpecsManager=None, swagger_specs_manager: SwaggerSpecsManager=None):
        self._aaz_specs = aaz_specs_manager
        self._swagger_specs = swagger_specs_manager

    @property
    def aaz_specs(self):
        if not self._aaz_specs:
            self._aaz_specs = AAZSpecsManager()
        return self._aaz_specs

    @property
    def swagger_specs(self):
        if not self._swagger_specs:
            self._swagger_specs = SwaggerSpecsManager()
        return self._swagger_specs

    def __call__(self, cli_profile: CLIViewProfile):
        profile = PSSketchProfile()
        profile.resource_providers = []
        for cli_command in self.iter_cli_commands(cli_profile):
            names = cli_command.names
            version_name = cli_command.version
            aaz_cmd = self.aaz_specs.find_command(*names)
            if not aaz_cmd:
                raise ResourceNotFind(
                    "Command '{}' not exist in AAZ".format(" ".join(names))
                )
            version = None
            for v in aaz_cmd.versions or []:
                if v.name == version_name:
                    version = v
                    break
            if not version:
                raise ResourceNotFind(
                    "Version '{}' of command '{}' not exist in AAZ".format(
                        version_name, " ".join(names)
                    )
                )
            resource = v.resources[0]
            cfg = self.aaz_specs.load_resource_cfg_reader(
                resource.plane, resource.id, resource.version
            )
            if not cfg:
                raise ResourceNotFind(
                    "Resource Configuration '{}' not exist in AAZ".format(resource.id)
                )
            for resource in cfg.resources:
                rp_swagger, _ = resource.swagger.split('/Paths/')
                rp = None
                for existing_rp in profile.resource_providers:
                    if existing_rp.swagger == rp_swagger:
                        rp = existing_rp
                        break
                if rp is None:
                    rp = PSSketchResourceProvider()
                    rp.swagger = rp_swagger
                    rp.resources = []
                    profile.resource_providers.append(rp)
                s_resource = None
                for existing_s_resource in rp.resources:
                    if existing_s_resource.id == resource.id:
                        s_resource = existing_s_resource
                        break
                if s_resource is None:
                    s_resource = PSSketchResource()
                    s_resource.id = resource.id
                    s_resource.path = resource.path
                    s_resource.cli_commands = []
                    s_resource.subresources = []
                    rp.resources.append(s_resource)
                s_resource.cli_commands.append(cli_command.__class__(raw_data=cli_command.to_native()))
                if resource.subresource:
                    s_resource.subresources.append(resource.subresource)
        return profile

    @classmethod
    def iter_cli_commands(cls, profile: CLIViewProfile):
        for command_group in profile.command_groups.values():
            for cli_command in cls._iter_cli_commands(command_group):
                yield cli_command

    @classmethod
    def _iter_cli_commands(cls, view_command_group):
        if view_command_group.commands:
            for cli_command in view_command_group.commands.values():
                yield cli_command
        if view_command_group.command_groups:
            for command_group in view_command_group.command_groups.values():
                for cli_command in cls._iter_cli_commands(command_group):
                    yield cli_command