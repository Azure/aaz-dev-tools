# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import logging

from cli.model.atomic import CLIAtomicProfile, CLIAtomicCommandGroup, CLIAtomicCommandGroupRegisterInfo, \
    CLIAtomicCommand, CLIAtomicCommandRegisterInfo, CLISpecsResource, CLICommandGroupHelp, CLICommandHelp, \
    CLICommandExample
from command.controller.cfg_reader import CfgReader
from command.controller.specs_manager import AAZSpecsManager
from command.model.configuration import CMDHttpOperation, CMDCommand, CMDArgGroup, CMDObjectOutput, \
    CMDHttpResponseJsonBody, CMDObjectSchemaBase
from swagger.utils.tools import swagger_resource_path_to_resource_id
from utils.stage import AAZStageEnum
from utils.exceptions import ResourceNotFind

logger = logging.getLogger('backend')


class AzAtomicProfileBuilder:

    def __init__(self):
        self._aaz_spec_manager = AAZSpecsManager()

    def __call__(self, view_profile):
        profile = CLIAtomicProfile()
        profile.name = view_profile.name
        if view_profile.command_groups:
            cmd_groups = {}
            for name, view_cmd_group in view_profile.command_groups.items():
                cmd_group = self._build_command_group(view_cmd_group)
                cmd_groups[name] = cmd_group
            profile.command_groups = cmd_groups
        return profile

    def _build_command_group(self, view_command_group):
        command_group = self._build_command_group_from_aaz(*view_command_group.names)
        stages = set()

        if view_command_group.commands:
            cmds = {}
            for name, view_cmd in view_command_group.commands.items():
                cmd = self._build_command(view_cmd)
                if cmd is None:
                    continue
                if cmd.register_info is not None:
                    stages.add(cmd.register_info.stage)
                cmds[name] = cmd
            command_group.commands = cmds

            self._complete_command_wait_info(command_group)

        if view_command_group.command_groups:
            cmd_groups = {}
            for name, view_cmd_group in view_command_group.command_groups.items():
                cmd_group = self._build_command_group(view_cmd_group)
                if cmd_group is None:
                    continue
                if cmd_group.register_info is not None:
                    stages.add(cmd_group.register_info.stage)
                cmd_groups[name] = cmd_group
            command_group.command_groups = cmd_groups

        if AAZStageEnum.Stable in stages:
            command_group.register_info.stage = AAZStageEnum.Stable
        elif AAZStageEnum.Preview in stages:
            command_group.register_info.stage = AAZStageEnum.Preview
        elif AAZStageEnum.Experimental in stages:
            command_group.register_info.stage = AAZStageEnum.Experimental
        elif not stages:
            command_group.register_info = None
        else:
            raise NotImplementedError()

        return command_group

    def _build_command(self, view_command):
        command = self._build_command_from_aaz(*view_command.names, version_name=view_command.version)
        if not view_command.registered:
            command.register_info = None
        return command

    def _build_command_group_from_aaz(self, *names):
        aaz_cg = self._aaz_spec_manager.find_command_group(*names)
        if not aaz_cg:
            raise ResourceNotFind("Command group '{}' not exist in AAZ".format(' '.join(names)))
        command_group = CLIAtomicCommandGroup()
        command_group.names = [*names]
        command_group.help = CLICommandGroupHelp()
        command_group.help.short = aaz_cg.help.short
        if aaz_cg.help.lines:
            command_group.help.long = '\n'.join(aaz_cg.help.lines)
        command_group.register_info = CLIAtomicCommandGroupRegisterInfo({
            "stage": AAZStageEnum.Stable
        })
        return command_group

    def _build_command_from_aaz(self, *names, version_name):
        aaz_cmd = self._aaz_spec_manager.find_command(*names)
        if not aaz_cmd:
            raise ResourceNotFind("Command '{}' not exist in AAZ".format(' '.join(names)))
        version = None
        for v in (aaz_cmd.versions or []):
            if v.name == version_name:
                version = v
                break
        if not version:
            raise ResourceNotFind("Version '{}' of command '{}' not exist in AAZ".format(version_name, ' '.join(names)))
        cfg_reader = self._aaz_spec_manager.load_resource_cfg_reader_by_command_with_version(aaz_cmd, version=version)
        cmd_cfg = cfg_reader.find_command(*names)
        assert cmd_cfg is not None, f"command model miss in AAZ: '{' '.join(names)}'"

        command = CLIAtomicCommand()
        command.names = [*names]
        command.help = CLICommandHelp()
        command.help.short = aaz_cmd.help.short
        if aaz_cmd.help.lines:
            command.help.long = '\n'.join(aaz_cmd.help.lines)

        if version.examples:
            command.help.examples = [CLICommandExample(e.to_primitive()) for e in version.examples]
        command.version = version.name
        command.stage = version.stage or AAZStageEnum.Stable
        command.cfg = cmd_cfg
        command.resources = [CLISpecsResource(r.to_primitive()) for r in version.resources]
        command.register_info = CLIAtomicCommandRegisterInfo({
            "stage": command.stage,
            "confirmation": cmd_cfg.confirmation,
        })

        if command.register_info is not None:
            command.register_info.confirmation = cmd_cfg.confirmation
        return command

    @classmethod
    def _complete_command_wait_info(cls, command_group):
        assert command_group.commands
        wait_cmd_rids = {}
        for command in command_group.commands.values():
            lro_list = []
            for operation in command.cfg.operations:
                if isinstance(operation, CMDHttpOperation):
                    if operation.long_running:
                        lro_list.append(operation)

            if len(lro_list) == 1:
                # support no wait if there are only one long running operation
                # not support multiple long running operations
                command.support_no_wait = True
                if command.register_info is not None:
                    # command is registered
                    rid = swagger_resource_path_to_resource_id(lro_list[0].http.path)
                    if rid not in wait_cmd_rids:
                        wait_cmd_rids[rid] = {
                            "methods": set()
                        }

        if not wait_cmd_rids:
            return

        # build wait command
        for command in command_group.commands.values():
            for operation in command.cfg.operations:
                # find get operations for wait command
                if not isinstance(operation, CMDHttpOperation):
                    continue
                rid = swagger_resource_path_to_resource_id(operation.http.path)
                if rid not in wait_cmd_rids:
                    continue
                if operation.http.request.method != 'get':
                    wait_cmd_rids[rid]['methods'].add(operation.http.request.method)
                    continue
                if 'get_op' in wait_cmd_rids[rid]:
                    continue

                # verify operation response has provisioning state field
                if not cls._has_provisioning_state(operation):
                    continue

                wait_cmd_rids[rid]['get_op'] = operation.__class__(operation.to_primitive())
                wait_cmd_rids[rid]['args'] = {}
                for resource in command.resources:
                    if rid == resource.id:
                        wait_cmd_rids[rid]['resource'] = resource.__class__(resource.to_primitive())

                params = []
                if operation.http.request.path and operation.http.request.path.params:
                    params += operation.http.request.path.params
                if operation.http.request.query and operation.http.request.query.params:
                    params += operation.http.request.query.params
                if operation.http.request.header and operation.http.request.header.params:
                    params += operation.http.request.header.params
                for param in params:
                    if not param.arg:
                        continue
                    assert param.arg.startswith("$"), f"Not support path arg name: '{param.arg}'"
                    arg, arg_idx = CfgReader.find_arg_in_command_by_var(
                        command=command.cfg,
                        arg_var=param.arg
                    )
                    assert arg is not None
                    wait_cmd_rids[rid]['args'][arg_idx] = arg.__class__(arg.to_primitive())

        for rid, value in [*wait_cmd_rids.items()]:
            if "get_op" not in value:
                logger.error(f'Failed to support wait command for resource: '
                             f'Get operation with provisioning state property does not exist: {rid}')
                del wait_cmd_rids[rid]

        if not wait_cmd_rids:
            return

        if len(wait_cmd_rids) > 1:
            # Not support to generate wait command for multiple resources
            logger.error(f'A wait command cannot apply on multiple resources')
            return

        wait_cmd_info = [*wait_cmd_rids.values()][0]

        command_group.wait_command = wait_command = CLIAtomicCommand()
        wait_command.names = [*command_group.names, "wait"]
        wait_command.help = CLICommandHelp()
        wait_command.help.short = "Place the CLI in a waiting state until a condition is met."
        wait_command.register_info = CLIAtomicCommandRegisterInfo()
        wait_command.resources = [wait_cmd_info['resource']]
        wait_command.cfg = cfg = CMDCommand()
        cfg.name = "wait"
        cfg.version = "undefined"

        arg_group = CMDArgGroup()
        cfg.arg_groups = [arg_group]
        arg_group.name = ""
        arg_group.args = [
            *wait_cmd_info['args'].values()
        ]
        get_op = wait_cmd_info['get_op']
        cfg.operations = [get_op]

        output = CMDObjectOutput()
        for response in get_op.http.responses:
            if response.is_error:
                continue
            if not isinstance(response.body, CMDHttpResponseJsonBody):
                continue
            if response.body.json.var:
                output.ref = response.body.json.var
                break
        if not output.ref:
            raise ValueError("Output ref is empty")
        output.client_flatten = False
        cfg.outputs = [output]

    @staticmethod
    def _has_provisioning_state(get_op):
        for response in get_op.http.responses:
            if response.is_error:
                continue
            if not isinstance(response.body, CMDHttpResponseJsonBody):
                continue
            if not isinstance(response.body.json.schema, CMDObjectSchemaBase):
                continue
            schema = response.body.json.schema
            if schema.props:
                for prop in schema.props:
                    if prop.name.lower() in ("provisioning_state", "provisioningstate"):
                        return True
                    if prop.name.lower() == "properties" and \
                            isinstance(prop, CMDObjectSchemaBase) and prop.props:
                        for sub_prop in prop.props:
                            if sub_prop.name.lower() in ("provisioning_state", "provisioningstate"):
                                return True
                            if sub_prop.name.lower() in ("additional_properties", "additionalproperties") and \
                                    isinstance(sub_prop, CMDObjectSchemaBase) and sub_prop.props:
                                for p in sub_prop.props:
                                    if p.name.lower() in ("provisioning_state", "provisioningstate"):
                                        return True
        return False
