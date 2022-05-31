import json
import os

from command.controller.workspace_cfg_editor import WorkspaceCfgEditor
from command.controller.workspace_manager import WorkspaceManager
from command.tests.common import CommandTestCase, workspace_name
from swagger.utils.tools import swagger_resource_path_to_resource_id
from utils.plane import PlaneEnum


class ArgumentsGenerationTest(CommandTestCase):

    @workspace_name("test_flatten_simple_object_argument")
    def test_flatten_simple_object_argument(self, ws_name):
        manager = WorkspaceManager.new(ws_name, plane=PlaneEnum.Mgmt)
        manager.save()

        mod_names = "edgeorder"

        manager.add_new_resources_by_swagger(
            mod_names=mod_names,
            version='2021-12-01',
            resources=[
                {
                    "id": swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/providers/Microsoft.EdgeOrder/addresses'),
                },
                {
                    "id": swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.EdgeOrder/addresses'),
                },
                {
                    "id": swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.EdgeOrder/addresses/{addressName}'),
                },
            ]
        )
        manager.save()
        cmd_names = ('edge-order', 'address', 'create')
        leaf = manager.find_command_tree_leaf(*cmd_names)
        cfg_editor = manager.load_cfg_editor_by_command(leaf)
        command = cfg_editor.find_command(*cmd_names)
        arg_var = '$addressResource.properties.contactDetails'
        arg = cfg_editor.find_arg(*cmd_names, arg_var=arg_var)
        assert arg is not None
        assert not arg.required
        assert cfg_editor.find_arg(*cmd_names, arg_var='$addressResource.properties.contactDetails.contactName').required is True

        properties = command.operations[0].http.request.body.json.schema.props[1]
        assert properties.props[0].arg == arg_var

        cfg_editor.flatten_arg(*cmd_names, arg_var=arg_var, sub_args_options={
            '$addressResource.properties.contactDetails.phoneExtension': ['phone-ext']
        })

        manager.save()
        cfg_editor = manager.load_cfg_editor_by_command(leaf)
        command = cfg_editor.find_command(*cmd_names)

        assert cfg_editor.find_arg(*cmd_names, arg_var=arg_var) is None

        properties = command.operations[0].http.request.body.json.schema.props[1]
        assert properties.props[0].arg is None

        arg = cfg_editor.find_arg(*cmd_names, arg_var='$addressResource.properties.contactDetails.phoneExtension')
        assert arg.options == ['phone-ext']
        assert not cfg_editor.find_arg(*cmd_names, arg_var='$addressResource.properties.contactDetails.contactName').required

        group = command.arg_groups[2]
        assert group.name == 'ContactDetails'

        cfg_editor.unflatten_arg(*cmd_names, arg_var=arg_var, options=['contact-address', 'address'], help={
            "short": "The contact address."
        })

        manager.save()
        cfg_editor = manager.load_cfg_editor_by_command(leaf)
        command = cfg_editor.find_command(*cmd_names)

        properties = command.operations[0].http.request.body.json.schema.props[1]
        assert properties.props[0].arg == arg_var
        assert len(command.arg_groups) == 3

        arg = cfg_editor.find_arg(*cmd_names, arg_var='$addressResource.properties.contactDetails.phoneExtension')
        assert arg.options == ['phone-ext']
        assert arg.group is None
        assert cfg_editor.find_arg(*cmd_names, arg_var='$addressResource.properties.contactDetails.contactName').required is True
