from command.controller.workspace_manager import WorkspaceManager
from command.tests.common import CommandTestCase, workspace_name
from swagger.utils.tools import swagger_resource_path_to_resource_id
from swagger.utils.source import SourceTypeEnum
from utils.plane import PlaneEnum
from utils import exceptions


class ArgumentsGenerationTest(CommandTestCase):

    @workspace_name("test_flatten_simple_object_argument")
    def test_flatten_simple_object_argument(self, ws_name):
        mod_names = "edgeorder"
        manager = WorkspaceManager.new(
            ws_name, plane=PlaneEnum.Mgmt, mod_names=mod_names, resource_provider="Microsoft.EdgeOrder", source=SourceTypeEnum.OpenAPI)
        manager.save()

        manager.add_new_resources_by_swagger(
            mod_names=mod_names,
            version='2021-12-01',
            resources=[
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
        arg, _ = cfg_editor.find_arg_by_var(*cmd_names, arg_var=arg_var)
        assert arg is not None
        assert not arg.required
        arg, _ = cfg_editor.find_arg_by_var(*cmd_names, arg_var='$addressResource.properties.contactDetails.contactName')
        assert arg.required is True

        properties = command.operations[0].http.request.body.json.schema.props[1]
        assert properties.props[0].arg == arg_var

        cfg_editor.flatten_arg(*cmd_names, arg_var=arg_var, sub_args_options={
            '$addressResource.properties.contactDetails.phoneExtension': ['phone-ext']
        })

        manager.save()
        cfg_editor = manager.load_cfg_editor_by_command(leaf)
        command = cfg_editor.find_command(*cmd_names)

        arg, _ = cfg_editor.find_arg_by_var(*cmd_names, arg_var=arg_var)
        assert arg is None

        properties = command.operations[0].http.request.body.json.schema.props[1]
        assert properties.props[0].arg is None

        arg, _ = cfg_editor.find_arg_by_var(*cmd_names, arg_var='$addressResource.properties.contactDetails.phoneExtension')
        assert arg.options == ['phone-ext']

        arg, _ = cfg_editor.find_arg_by_var(*cmd_names, arg_var='$addressResource.properties.contactDetails.contactName')
        assert not arg.required

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

        arg, _ = cfg_editor.find_arg_by_var(*cmd_names, arg_var='$addressResource.properties.contactDetails.phoneExtension')
        assert arg.options == ['phone-ext']
        assert arg.group is None
        arg, _ = cfg_editor.find_arg_by_var(*cmd_names, arg_var='$addressResource.properties.contactDetails.contactName')
        assert arg.required is True

    @workspace_name("test_flatten_object_argument_invalid")
    def test_flatten_object_argument_invalid(self, ws_name):
        mod_names = "edgeorder"
        manager = WorkspaceManager.new(
            ws_name, plane=PlaneEnum.Mgmt, mod_names=mod_names, resource_provider="Microsoft.EdgeOrder", source=SourceTypeEnum.OpenAPI)
        manager.save()



        manager.add_new_resources_by_swagger(
            mod_names=mod_names,
            version='2021-12-01',
            resources=[
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
        arg, _ = cfg_editor.find_arg_by_var(*cmd_names, arg_var=arg_var)
        assert arg is not None
        assert not arg.required
        arg, _ = cfg_editor.find_arg_by_var(
            *cmd_names, arg_var='$addressResource.properties.contactDetails.contactName')
        assert arg.required is True

        properties = command.operations[0].http.request.body.json.schema.props[1]
        assert properties.props[0].arg == arg_var

        with self.assertRaises(exceptions.InvalidAPIUsage):
            cfg_editor.flatten_arg(*cmd_names, arg_var=arg_var, sub_args_options={
                '$addressResource.properties.contactDetails.contactName': ['contact-name', 'name']
            })

        # manager = WorkspaceManager(ws_name)
        cfg_editor = manager.load_cfg_editor_by_command(leaf, reload=True)
        cfg_editor.flatten_arg(*cmd_names, arg_var=arg_var, sub_args_options={
            '$addressResource.properties.contactDetails.contactName': ['contact-name']
        })

        manager.save()
        cfg_editor = manager.load_cfg_editor_by_command(leaf)
        command = cfg_editor.find_command(*cmd_names)

        with self.assertRaises(exceptions.InvalidAPIUsage):
            cfg_editor.unflatten_arg(*cmd_names, arg_var=arg_var, options=['contact-address', 'address'], help={
                "short": "The contact address."
            }, sub_args_options={
                '$addressResource.properties.contactDetails.contactName': ['contact-name', 'name'],
                '$addressResource.properties.contactDetails.phoneExtension': ['phone-ext', 'name'],
            })

