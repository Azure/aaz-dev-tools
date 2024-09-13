from .az_module_manager import AzModuleManager
from swagger.controller.specs_manager import SwaggerSpecsManager
from command.controller.specs_manager import AAZSpecsManager
from utils.config import Config
from utils.exceptions import ResourceNotFind
from command.model.configuration import CMDConfiguration, CMDResource, CMDHttpOperation
import json
import logging
import inflect
import re
from swagger.model.specs._utils import map_path_2_repo

from fuzzywuzzy import fuzz


logger = logging.getLogger('backend')


class PSAutoRestConfigurationGenerator:
    _CAMEL_CASE_PATTERN = re.compile(r"^([a-zA-Z][a-z0-9]+)(([A-Z][a-z0-9]*)+)$")
    _inflect_engine = inflect.engine()

    def __init__(self, az_module_manager: AzModuleManager, module_name) -> None:
        self.module_manager = az_module_manager
        self.module_name = module_name
        self.aaz_specs_manager = AAZSpecsManager()
        self.swagger_specs_manager = SwaggerSpecsManager()
        self._ps_profile = None

    def generate_config(self):
        module = self.module_manager.load_module(self.module_name)

        cli_profile = {}

        for cli_command in self.iter_cli_commands(module.profiles[Config.CLI_DEFAULT_PROFILE]):
            names = cli_command.names
            version_name = cli_command.version
            aaz_cmd = self.aaz_specs_manager.find_command(*names)
            if not aaz_cmd:
                raise ResourceNotFind("Command '{}' not exist in AAZ".format(' '.join(names)))
            version = None
            for v in (aaz_cmd.versions or []):
                if v.name == version_name:
                    version = v
                    break
            if not version:
                raise ResourceNotFind("Version '{}' of command '{}' not exist in AAZ".format(version_name, ' '.join(names)))
            resource = v.resources[0]
            cfg: CMDConfiguration = self.aaz_specs_manager.load_resource_cfg_reader(resource.plane, resource.id, resource.version)
            if not cfg:
                raise ResourceNotFind("Resource Configuration '{}' not exist in AAZ".format(resource.id))
            for resource in cfg.resources:
                tag = (resource.plane, '/'.join(resource.mod_names), resource.rp_name)
                if tag not in cli_profile:
                    cli_profile[tag] = {}
                if resource.id not in cli_profile[tag]:
                    cli_profile[tag][resource.id] = {
                        "path": resource.path,
                        "cfg": cfg,
                        "commands": [],
                        "subresources": [],
                    }
                cli_profile[tag][resource.id]["commands"].append(cli_command.names)
                if resource.subresource:
                    cli_profile[tag][resource.id]["subresources"].append(resource.subresource)
        
        # TODO: let LLM to choice the plane and rp_name later
        if len(cli_profile.keys()) > 1:
            raise ValueError("Only one plane module and rp_name is supported")
        (plane, mod_names, rp_name) = list(cli_profile.keys())[0]
        cli_resources = cli_profile[(plane, mod_names, rp_name)]

        module_manager = self.swagger_specs_manager.get_module_manager(plane, mod_names.split('/'))
        rp = module_manager.get_openapi_resource_provider(rp_name)
        swagger_resources = rp.get_resource_map_by_tag(rp.default_tag)
        if not swagger_resources:
            raise ResourceNotFind("Resources not find in Swagger")
        
        ps_profile = {}

        for resource_id, resource in swagger_resources.items():
            resource = list(resource.values())[0]
            op_group_name = self.get_operation_group_name(resource)
            if op_group_name not in ps_profile:
                ps_profile[op_group_name] = {
                    "operations": {},
                }
            if resource_id not in cli_resources:
                for op_tag, method in resource.operations.items():
                    ps_profile[op_group_name]["operations"][op_tag] = {
                        "tag": op_tag,
                        "delete": True,
                        "method": method,
                    }
            else:
                for cmd_names in cli_resources[resource_id]["commands"]:
                    cfg = cli_resources[resource_id]["cfg"]
                    command = cfg.find_command(*cmd_names)
                    assert command is not None
                    for cmd_op in command.operations:
                        if not isinstance(cmd_op, CMDHttpOperation):
                            continue
                        op_tag = cmd_op.operation_id
                        if op_tag not in resource.operations:
                            continue
                        method = resource.operations[op_tag]
                        ps_profile[op_group_name]["operations"][op_tag] = {
                            "delete": False,
                            "method": method,
                        }
                for op_tag, method in resource.operations.items():
                    if op_tag not in ps_profile[op_group_name]["operations"]:
                        ps_profile[op_group_name]["operations"][op_tag] = {
                            "delete": False if method == "patch" else True,  # PowerShell Prefer Patch Method for update commands
                            "method": method,
                        }
        
        for group in ps_profile.values():
            delete_all = True
            for op_tag, op in group["operations"].items():
                if not op["delete"]:
                    delete_all = False
                    break
            group["delete"] = delete_all

        self._ps_profile = ps_profile
        # # write to json file
        # with open("ps_profile.json", 'w') as f:
        #     json.dump(ps_profile, f, indent=4)

    def iter_cli_commands(self, profile):
        for command_group in profile.command_groups.values():
            for cli_command in self._iter_cli_commands(command_group):
                yield cli_command

    def _iter_cli_commands(self, view_command_group):
        if view_command_group.commands:
            for cli_command in view_command_group.commands.values():
                yield cli_command
        if view_command_group.command_groups:
            for command_group in view_command_group.command_groups.values():
                for cli_command in self._iter_cli_commands(command_group):
                    yield cli_command

    def get_operation_group_name(self, resource):

        operation_groups = set()
        for operation_id, method in resource.operations.items():
            op_group = self._parse_operation_group_name(resource, operation_id, method)
            operation_groups.add(op_group)

        if None in operation_groups:
            return None

        if len(operation_groups) == 1:
            return operation_groups.pop()

        op_group_name = sorted(
            operation_groups,
            key=lambda nm: fuzz.partial_ratio(resource.id, nm),  # use the name which is closest to resource_id
            reverse=True
        )[0]
        return op_group_name

    def _parse_operation_group_name(self, resource, op_id, method):
        # extract operation group name from operation_id
        value = op_id.strip()
        value = value.replace('-', '_')
        if '_' in value:
            parts = value.split('_')
            op_group_name = parts[0]
            if op_group_name.lower() in ("create", "get", "update", "delete", "patch"):
                op_group_name = parts[1]
        else:
            if ' ' in value:
                value = value.replace(' ', '')  # Changed to Camel Case
            match = self._CAMEL_CASE_PATTERN.match(value)
            if not match:
                logger.error(f"InvalidOperationIdFormat:"
                             f"\toperationId should be in format of '[OperationGroupName]_[OperationName]' "
                             f"or '[Verb][OperationGroupName]':\n"
                             f"\tfile: {map_path_2_repo(resource.file_path)}\n"
                             f"\tpath: {resource.path}\n"
                             f"\tmethod: {method} operationId: {op_id}\n")
                return None
            op_group_name = match[2]  # [OperationGroupName]

        return self._inflect_engine.singular_noun(op_group_name) or op_group_name
