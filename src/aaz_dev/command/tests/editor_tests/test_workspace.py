from command.controller.workspace_manager import WorkspaceManager
from command.controller.cfg_reader import _SchemaIdxEnum
from command.tests.common import CommandTestCase, workspace_name
from utils.plane import PlaneEnum
import os
import json
from utils import exceptions
from swagger.utils.tools import swagger_resource_path_to_resource_id


class WorkspaceManagerTest(CommandTestCase):

    @workspace_name("test_workspace_manager")
    def test_workspace_manager(self, ws_name):
        manager = WorkspaceManager(ws_name)
        assert manager.path.endswith(os.path.join(ws_name, "ws.json"))

        manager = WorkspaceManager.new(ws_name, plane=PlaneEnum.Mgmt)
        manager.save()
        assert os.path.exists(manager.path)
        with open(manager.path, 'r') as f:
            data = json.load(f)
        assert data['name'] == ws_name
        assert data['plane'] == PlaneEnum.Mgmt
        assert data['version']
        assert data['commandTree'] == {
            "names": ['aaz']
        }

        manager_2 = WorkspaceManager(ws_name)
        manager_2.load()
        assert manager_2.ws.name == ws_name
        assert manager_2.ws.plane == PlaneEnum.Mgmt
        assert manager_2.ws.version == manager.ws.version
        assert manager_2.ws.command_tree.names == ['aaz']
        manager_2.save()

        with self.assertRaises(exceptions.InvalidAPIUsage):
            manager.save()


class WorkspaceEditorTest(CommandTestCase):

    @workspace_name("test_workspace_editor_add_resources_by_swagger")
    def test_workspace_editor_add_resources_by_swagger(self, ws_name):
        manager = WorkspaceManager.new(ws_name, plane=PlaneEnum.Mgmt)
        manager.save()

        mod_names = "edgeorder"

        manager.add_new_resources_by_swagger(
            mod_names=mod_names,
            version='2021-12-01',
            resources=[
                {
                    "id": swagger_resource_path_to_resource_id('/subscriptions/{subscriptionId}/providers/Microsoft.EdgeOrder/addresses'),
                },
                {
                    "id": swagger_resource_path_to_resource_id('/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.EdgeOrder/addresses'),
                },
                {
                    "id": swagger_resource_path_to_resource_id('/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.EdgeOrder/addresses/{addressName}'),
                }
            ]
        )
        manager.save()

        manager = WorkspaceManager(ws_name)
        manager.load()
        assert 'edge-order' in manager.ws.command_tree.command_groups
        assert 'address' in manager.ws.command_tree.command_groups['edge-order'].command_groups
        address_cg = manager.ws.command_tree.command_groups['edge-order'].command_groups['address']
        assert 'list' in address_cg.commands and len(address_cg.commands['list'].resources) == 2
        assert 'create' in address_cg.commands and len(address_cg.commands['create'].resources) == 1
        assert 'show' in address_cg.commands and len(address_cg.commands['show'].resources) == 1
        assert 'delete' in address_cg.commands and len(address_cg.commands['delete'].resources) == 1
        assert 'update' in address_cg.commands and len(address_cg.commands['update'].resources) == 1

        assert manager.load_cfg_editor_by_command(address_cg.commands['list'])
        assert manager.load_cfg_editor_by_command(address_cg.commands['create'])
        assert manager.load_cfg_editor_by_command(address_cg.commands['show'])
        assert manager.load_cfg_editor_by_command(address_cg.commands['delete'])
        assert manager.load_cfg_editor_by_command(address_cg.commands['update'])

    @workspace_name("test_workspace_editor_subresource")
    def test_workspace_editor_subresource(self, ws_name):

        manager = WorkspaceManager.new(ws_name, plane=PlaneEnum.Mgmt)
        manager.save()

        mod_names = "cdn"
        version = '2021-06-01'
        resource_id = swagger_resource_path_to_resource_id('/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Cdn/profiles/{profileName}/endpoints/{endpointName}')

        manager.add_new_resources_by_swagger(
            mod_names=mod_names,
            version=version,
            resources=[
                {
                    "id": resource_id
                },
                {
                    "id": swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Cdn/profiles/{profileName}/endpoints'),
                }
            ]
        )
        manager.save()

        manager = WorkspaceManager(ws_name)
        manager.load()

        cfg = manager.load_cfg_editor_by_resource(resource_id, version)
        create_cmd = cfg.find_command("cdn", "profile", "endpoint", "create")
        update_cmd = cfg.find_command("cdn", "profile", "endpoint", "update")

        arg_var = '$endpoint.properties.originGroups'

        count = 0
        for parent_schema, schema, schema_idx in cfg.iter_schema_in_command_by_arg_var(create_cmd, arg_var):
            count += 1
            self.assertEqual(schema.name, "originGroups")
            self.assertEqual(schema_idx[-3:], [_SchemaIdxEnum.Json, 'properties', 'originGroups'])
            self.assertEqual(schema.identifiers, ['name'])
        self.assertEqual(count, 1)
        for parent_schema, schema, schema_idx in cfg.iter_schema_in_command_by_arg_var(update_cmd, arg_var):
            count += 1
            self.assertEqual(schema.name, "originGroups")
            self.assertEqual(schema_idx[-3:], [_SchemaIdxEnum.Json, 'properties', 'originGroups'])
            self.assertEqual(schema.identifiers, ['name'])
        self.assertEqual(count, 2)

        cfg.build_subresource_commands_by_arg_var(resource_id, arg_var, cg_names=["cdn", "profile", "endpoint", 'origin-group'])

        arg_var = '$endpoint.properties.originGroups[].properties.origins'

        count = 0
        for parent_schema, schema, schema_idx in cfg.iter_schema_in_command_by_arg_var(create_cmd, arg_var):
            count += 1
            self.assertEqual(schema.name, "origins")
            self.assertEqual(schema_idx[-6:], [_SchemaIdxEnum.Json, 'properties', 'originGroups', '[]', 'properties', 'origins'])
        self.assertEqual(count, 1)
        for parent_schema, schema, schema_idx in cfg.iter_schema_in_command_by_arg_var(update_cmd, arg_var):
            count += 1
            self.assertEqual(schema.name, "origins")
            self.assertEqual(schema_idx[-6:], [_SchemaIdxEnum.Json, 'properties', 'originGroups', '[]', 'properties', 'origins'])
        self.assertEqual(count, 2)

        cfg.build_subresource_commands_by_arg_var(resource_id, arg_var, cg_names=["cdn", "profile", "endpoint", 'origin-group', 'origin'])

