from command.controller.workspace_manager import WorkspaceManager
from command.controller.cfg_reader import _SchemaIdxEnum
from command.tests.common import CommandTestCase, workspace_name
from utils.plane import PlaneEnum
import os
import json
from utils import exceptions
from swagger.utils.tools import swagger_resource_path_to_resource_id
from swagger.utils.source import SourceTypeEnum
from command.model.configuration import *


class WorkspaceManagerTest(CommandTestCase):

    @workspace_name("test_workspace_manager")
    def test_workspace_manager(self, ws_name):
        manager = WorkspaceManager(ws_name)
        assert manager.path.endswith(os.path.join(ws_name, "ws.json"))

        mod_names = "edgeorder"
        resource_provider = 'Microsoft.EdgeOrder'
        manager = WorkspaceManager.new(ws_name, plane=PlaneEnum.Mgmt, mod_names=mod_names, resource_provider=resource_provider, source=SourceTypeEnum.OpenAPI)
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
        mod_names = "edgeorder"
        resource_provider = 'Microsoft.EdgeOrder'
        manager = WorkspaceManager.new(ws_name, plane=PlaneEnum.Mgmt, mod_names=mod_names, resource_provider=resource_provider, source=SourceTypeEnum.OpenAPI)
        manager.save()


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
        mod_names = "cdn"
        resource_provider = "Microsoft.Cdn"
        manager = WorkspaceManager.new(ws_name, plane=PlaneEnum.Mgmt, mod_names=mod_names, resource_provider=resource_provider, source=SourceTypeEnum.OpenAPI)
        manager.save()

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

        # az cdn profile endpoint origin-group
        cfg.build_subresource_commands_by_arg_var(resource_id, arg_var, cg_names=["cdn", "profile", "endpoint", 'origin-group'])

        list_command = cfg.find_command("cdn", "profile", "endpoint", 'origin-group', 'list')

        self.assertTrue(list_command is not None)
        subresource_selector = list_command.subresource_selector
        self.assertTrue(isinstance(subresource_selector, CMDJsonSubresourceSelector))
        self.assertEqual(subresource_selector.ref, "$Instance")
        self.assertEqual(subresource_selector.var, "$Subresource")
        self.assertTrue(isinstance(subresource_selector.json, CMDObjectIndex))
        self.assertEqual(subresource_selector.json.name, "endpoint")
        self.assertTrue(isinstance(subresource_selector.json.prop, CMDArrayIndex))
        self.assertEqual(subresource_selector.json.prop.name, "properties.originGroups")
        self.assertEqual(subresource_selector.json.prop.identifiers, None)
        self.assertEqual(subresource_selector.json.prop.item, None)

        self.assertEqual(len(list_command.arg_groups), 1)
        args_var_set = set()
        for arg in list_command.arg_groups[0].args:
            args_var_set.add(arg.var)
        self.assertEqual(args_var_set, {
            '$Path.endpointName', '$Path.profileName', '$Path.resourceGroupName', '$Path.subscriptionId'})

        self.assertEqual(list_command.outputs[0].ref, '$Subresource')

        show_command = cfg.find_command("cdn", "profile", "endpoint", 'origin-group', 'show')
        self.assertTrue(show_command is not None)
        subresource_selector = show_command.subresource_selector
        self.assertTrue(isinstance(subresource_selector, CMDJsonSubresourceSelector))
        self.assertEqual(subresource_selector.ref, "$Instance")
        self.assertEqual(subresource_selector.var, "$Subresource")
        self.assertTrue(isinstance(subresource_selector.json, CMDObjectIndex))
        self.assertEqual(subresource_selector.json.name, "endpoint")
        self.assertTrue(isinstance(subresource_selector.json.prop, CMDArrayIndex))
        self.assertEqual(subresource_selector.json.prop.name, "properties.originGroups")
        self.assertEqual(len(subresource_selector.json.prop.identifiers), 1)
        identifier = subresource_selector.json.prop.identifiers[0]
        self.assertTrue(isinstance(identifier, CMDStringSchema))
        self.assertEqual(identifier.name, '[].name')
        self.assertEqual(identifier.arg, '$endpoint.properties.originGroups[].name')
        self.assertTrue(isinstance(subresource_selector.json.prop.item, CMDObjectIndexBase))
        self.assertEqual(subresource_selector.json.prop.item.additional_props, None)
        self.assertEqual(subresource_selector.json.prop.item.discriminator, None)
        self.assertEqual(subresource_selector.json.prop.item.prop, None)

        self.assertEqual(len(show_command.arg_groups), 1)
        args_var_set = set()
        for arg in show_command.arg_groups[0].args:
            args_var_set.add(arg.var)
        self.assertEqual(args_var_set, {
            '$Path.endpointName', '$Path.profileName', '$Path.resourceGroupName', '$Path.subscriptionId',
            '$endpoint.properties.originGroups[].name'})

        self.assertEqual(show_command.outputs[0].ref, '$Subresource')

        delete_command = cfg.find_command("cdn", "profile", "endpoint", 'origin-group', 'delete')
        self.assertTrue(delete_command is not None)
        subresource_selector = delete_command.subresource_selector
        self.assertTrue(isinstance(subresource_selector, CMDJsonSubresourceSelector))
        self.assertEqual(subresource_selector.ref, "$Instance")
        self.assertEqual(subresource_selector.var, "$Subresource")
        self.assertTrue(isinstance(subresource_selector.json, CMDObjectIndex))
        self.assertEqual(subresource_selector.json.name, "endpoint")
        self.assertTrue(isinstance(subresource_selector.json.prop, CMDArrayIndex))
        self.assertEqual(subresource_selector.json.prop.name, "properties.originGroups")
        self.assertEqual(len(subresource_selector.json.prop.identifiers), 1)
        identifier = subresource_selector.json.prop.identifiers[0]
        self.assertTrue(isinstance(identifier, CMDStringSchema))
        self.assertEqual(identifier.name, '[].name')
        self.assertEqual(identifier.arg, '$endpoint.properties.originGroups[].name')
        self.assertTrue(isinstance(subresource_selector.json.prop.item, CMDObjectIndexBase))
        self.assertEqual(subresource_selector.json.prop.item.additional_props, None)
        self.assertEqual(subresource_selector.json.prop.item.discriminator, None)
        self.assertEqual(subresource_selector.json.prop.item.prop, None)

        self.assertEqual(len(delete_command.arg_groups), 1)
        args_var_set = set()
        for arg in delete_command.arg_groups[0].args:
            args_var_set.add(arg.var)
        self.assertEqual(args_var_set, {
            '$Path.endpointName', '$Path.profileName', '$Path.resourceGroupName', '$Path.subscriptionId',
            '$endpoint.properties.originGroups[].name'})

        instance_delete = None
        for op in delete_command.operations:
            if isinstance(op, CMDInstanceDeleteOperation):
                assert not instance_delete
                instance_delete = op.instance_delete
        self.assertTrue(isinstance(instance_delete, CMDJsonInstanceDeleteAction))
        self.assertEqual(instance_delete.ref, '$Subresource')
        self.assertEqual(delete_command.outputs, None)

        create_command = cfg.find_command("cdn", "profile", "endpoint", 'origin-group', 'create')
        subresource_selector = create_command.subresource_selector
        self.assertTrue(isinstance(subresource_selector, CMDJsonSubresourceSelector))
        self.assertEqual(subresource_selector.ref, "$Instance")
        self.assertEqual(subresource_selector.var, "$Subresource")
        self.assertTrue(isinstance(subresource_selector.json, CMDObjectIndex))
        self.assertEqual(subresource_selector.json.name, "endpoint")
        self.assertTrue(isinstance(subresource_selector.json.prop, CMDArrayIndex))
        self.assertEqual(subresource_selector.json.prop.name, "properties.originGroups")
        self.assertEqual(len(subresource_selector.json.prop.identifiers), 1)
        identifier = subresource_selector.json.prop.identifiers[0]
        self.assertTrue(isinstance(identifier, CMDStringSchema))
        self.assertEqual(identifier.name, '[].name')
        self.assertEqual(identifier.arg, '$endpoint.properties.originGroups[].name')
        self.assertTrue(isinstance(subresource_selector.json.prop.item, CMDObjectIndexBase))
        self.assertEqual(subresource_selector.json.prop.item.additional_props, None)
        self.assertEqual(subresource_selector.json.prop.item.discriminator, None)
        self.assertEqual(subresource_selector.json.prop.item.prop, None)

        self.assertEqual(len(create_command.arg_groups), 2)
        args_var_set = set()
        for arg_group in create_command.arg_groups:
            for arg in arg_group.args:
                args_var_set.add(arg.var)
                if arg.var == '$Path.endpointName':
                    self.assertEqual(arg.options, ['endpoint-name'])
                elif arg.var == '$endpoint.properties.originGroups[].name':
                    self.assertFalse(arg.nullable)
                elif arg.var == '$endpoint.properties.originGroups[].properties.origins':
                    self.assertFalse(arg.item.nullable)
                elif arg.var.startswith('$endpoint.properties.originGroups[]'):
                    self.assertFalse(arg.nullable)
        self.assertEqual(args_var_set, {
            '$Path.endpointName', '$Path.profileName', '$Path.resourceGroupName', '$Path.subscriptionId',
            '$endpoint.properties.originGroups[].name', '$endpoint.properties.originGroups[].properties.healthProbeSettings',
            '$endpoint.properties.originGroups[].properties.origins', '$endpoint.properties.originGroups[].properties.responseBasedOriginErrorDetectionSettings',
            '$endpoint.properties.originGroups[].properties.trafficRestorationTimeToHealedOrNewEndpointsInMinutes'
        })
        instance_create = None
        for op in create_command.operations:
            if isinstance(op, CMDInstanceCreateOperation):
                assert not instance_create
                instance_create = op.instance_create
        self.assertTrue(isinstance(instance_create, CMDJsonInstanceCreateAction))
        self.assertEqual(instance_create.ref, '$Subresource')
        self.assertEqual(instance_create.json.schema.name, 'endpoint.properties.originGroups[]')
        self.assertEqual(create_command.outputs[0].ref, '$Subresource')

        update_command = cfg.find_command("cdn", "profile", "endpoint", 'origin-group', 'update')
        subresource_selector = update_command.subresource_selector
        self.assertTrue(isinstance(subresource_selector, CMDJsonSubresourceSelector))
        self.assertEqual(subresource_selector.ref, "$Instance")
        self.assertEqual(subresource_selector.var, "$Subresource")
        self.assertTrue(isinstance(subresource_selector.json, CMDObjectIndex))
        self.assertEqual(subresource_selector.json.name, "endpoint")
        self.assertTrue(isinstance(subresource_selector.json.prop, CMDArrayIndex))
        self.assertEqual(subresource_selector.json.prop.name, "properties.originGroups")
        self.assertEqual(len(subresource_selector.json.prop.identifiers), 1)
        identifier = subresource_selector.json.prop.identifiers[0]
        self.assertTrue(isinstance(identifier, CMDStringSchema))
        self.assertEqual(identifier.name, '[].name')
        self.assertEqual(identifier.arg, '$endpoint.properties.originGroups[].name')
        self.assertTrue(isinstance(subresource_selector.json.prop.item, CMDObjectIndexBase))
        self.assertEqual(subresource_selector.json.prop.item.additional_props, None)
        self.assertEqual(subresource_selector.json.prop.item.discriminator, None)
        self.assertEqual(subresource_selector.json.prop.item.prop, None)

        self.assertEqual(len(update_command.arg_groups), 2)
        args_var_set = set()
        for arg_group in update_command.arg_groups:
            for arg in arg_group.args:
                args_var_set.add(arg.var)
                if arg.var == '$Path.endpointName':
                    self.assertEqual(arg.options, ['endpoint-name'])
                if arg.var == '$endpoint.properties.originGroups[].name':
                    self.assertFalse(arg.nullable)
                elif arg.var == '$endpoint.properties.originGroups[].properties.origins':
                    self.assertTrue(arg.item.nullable)
                elif arg.var.startswith('$endpoint.properties.originGroups[]'):
                    self.assertTrue(arg.nullable)
        self.assertEqual(args_var_set, {
            '$Path.endpointName', '$Path.profileName', '$Path.resourceGroupName', '$Path.subscriptionId',
            '$endpoint.properties.originGroups[].name',
            '$endpoint.properties.originGroups[].properties.healthProbeSettings',
            '$endpoint.properties.originGroups[].properties.origins',
            '$endpoint.properties.originGroups[].properties.responseBasedOriginErrorDetectionSettings',
            '$endpoint.properties.originGroups[].properties.trafficRestorationTimeToHealedOrNewEndpointsInMinutes'
        })
        instance_update = None
        for op in update_command.operations:
            if isinstance(op, CMDInstanceUpdateOperation):
                assert not instance_update
                instance_update = op.instance_update
        self.assertTrue(isinstance(instance_update, CMDJsonInstanceUpdateAction))
        self.assertEqual(instance_update.ref, '$Subresource')
        self.assertEqual(instance_update.json.schema.name, 'endpoint.properties.originGroups[]')
        self.assertEqual(update_command.outputs[0].ref, '$Subresource')

    @workspace_name("test_workspace_editor_subresource_with_index")
    def test_workspace_editor_subresource_with_index(self, ws_name):
        mod_names = "cdn"
        resource_provider = "Microsoft.Cdn"
        manager = WorkspaceManager.new(ws_name, plane=PlaneEnum.Mgmt, mod_names=mod_names, resource_provider=resource_provider, source=SourceTypeEnum.OpenAPI)
        manager.save()

        version = '2021-06-01'
        resource_id = swagger_resource_path_to_resource_id(
            '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Cdn/profiles/{profileName}/endpoints/{endpointName}')

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

        # az cdn profile endpoint origin-group origin
        with self.assertRaises(exceptions.InvalidAPIUsage):
            cfg.build_subresource_commands_by_arg_var(resource_id, arg_var, cg_names=["cdn", "profile", "endpoint", 'origin-group', 'origin'])

        cfg.unwrap_cls_arg('cdn', 'profile', 'endpoint', 'update', arg_var=f"{arg_var}[]")
        cfg.build_subresource_commands_by_arg_var(
            resource_id, arg_var,cg_names=["cdn", "profile", "endpoint", 'origin-group', 'origin'])

        list_command = cfg.find_command("cdn", "profile", "endpoint", 'origin-group', 'origin', 'list')
        self.assertTrue(list_command is not None)
        subresource_selector = list_command.subresource_selector
        self.assertTrue(isinstance(subresource_selector, CMDJsonSubresourceSelector))
        self.assertEqual(subresource_selector.ref, "$Instance")
        self.assertEqual(subresource_selector.var, "$Subresource")
        self.assertTrue(isinstance(subresource_selector.json, CMDObjectIndex))
        self.assertEqual(subresource_selector.json.name, "endpoint")
        self.assertTrue(isinstance(subresource_selector.json.prop, CMDArrayIndex))
        self.assertEqual(subresource_selector.json.prop.name, "properties.originGroups")
        self.assertEqual(len(subresource_selector.json.prop.identifiers), 1)
        identifier = subresource_selector.json.prop.identifiers[0]
        self.assertTrue(isinstance(identifier, CMDStringSchema))
        self.assertEqual(identifier.name, '[].name')
        self.assertEqual(identifier.arg, '$endpoint.properties.originGroups[].name')
        self.assertTrue(isinstance(subresource_selector.json.prop.item, CMDObjectIndexBase))
        self.assertEqual(subresource_selector.json.prop.item.additional_props, None)
        self.assertEqual(subresource_selector.json.prop.item.discriminator, None)
        self.assertTrue(isinstance(subresource_selector.json.prop.item.prop, CMDArrayIndex))
        self.assertEqual(subresource_selector.json.prop.item.prop.name, 'properties.origins')
        self.assertEqual(subresource_selector.json.prop.item.prop.identifiers, None)
        self.assertEqual(subresource_selector.json.prop.item.prop.item, None)

        self.assertEqual(len(list_command.arg_groups), 1)
        args_var_set = set()
        for arg in list_command.arg_groups[0].args:
            args_var_set.add(arg.var)
        self.assertEqual(args_var_set, {
            '$Path.endpointName', '$Path.profileName', '$Path.resourceGroupName', '$Path.subscriptionId',
            '$endpoint.properties.originGroups[].name'})

        self.assertEqual(list_command.outputs[0].ref, '$Subresource')

        show_command = cfg.find_command("cdn", "profile", "endpoint", 'origin-group', 'origin', 'show')
        self.assertTrue(show_command is not None)
        subresource_selector = show_command.subresource_selector
        self.assertTrue(isinstance(subresource_selector, CMDJsonSubresourceSelector))
        self.assertEqual(subresource_selector.ref, "$Instance")
        self.assertEqual(subresource_selector.var, "$Subresource")
        self.assertTrue(isinstance(subresource_selector.json, CMDObjectIndex))
        self.assertEqual(subresource_selector.json.name, "endpoint")
        self.assertTrue(isinstance(subresource_selector.json.prop, CMDArrayIndex))
        self.assertEqual(subresource_selector.json.prop.name, "properties.originGroups")
        self.assertEqual(len(subresource_selector.json.prop.identifiers), 1)
        identifier = subresource_selector.json.prop.identifiers[0]
        self.assertTrue(isinstance(identifier, CMDStringSchema))
        self.assertEqual(identifier.name, '[].name')
        self.assertEqual(identifier.arg, '$endpoint.properties.originGroups[].name')
        self.assertTrue(isinstance(subresource_selector.json.prop.item, CMDObjectIndexBase))
        self.assertEqual(subresource_selector.json.prop.item.additional_props, None)
        self.assertEqual(subresource_selector.json.prop.item.discriminator, None)
        self.assertTrue(isinstance(subresource_selector.json.prop.item.prop, CMDArrayIndex))
        self.assertEqual(subresource_selector.json.prop.item.prop.name, 'properties.origins')
        identifier = subresource_selector.json.prop.item.prop.identifiers[0]
        self.assertTrue(isinstance(identifier, CMDIntegerSchema))
        self.assertEqual(identifier.name, '[Index]')
        self.assertEqual(identifier.arg, '$endpoint.properties.originGroups[].properties.origins[Index]')
        self.assertTrue(isinstance(subresource_selector.json.prop.item.prop.item, CMDObjectIndexBase))
        self.assertEqual(subresource_selector.json.prop.item.prop.item.additional_props, None)
        self.assertEqual(subresource_selector.json.prop.item.prop.item.discriminator, None)

        self.assertEqual(len(show_command.arg_groups), 1)
        args_var_set = set()
        for arg in show_command.arg_groups[0].args:
            args_var_set.add(arg.var)
        self.assertEqual(args_var_set, {
            '$Path.endpointName', '$Path.profileName', '$Path.resourceGroupName', '$Path.subscriptionId',
            '$endpoint.properties.originGroups[].name', '$endpoint.properties.originGroups[].properties.origins[Index]'})

        self.assertEqual(show_command.outputs[0].ref, '$Subresource')

        delete_command = cfg.find_command("cdn", "profile", "endpoint", 'origin-group', 'origin', 'delete')
        self.assertTrue(delete_command is not None)
        subresource_selector = delete_command.subresource_selector
        self.assertTrue(isinstance(subresource_selector, CMDJsonSubresourceSelector))
        self.assertEqual(subresource_selector.ref, "$Instance")
        self.assertEqual(subresource_selector.var, "$Subresource")
        self.assertTrue(isinstance(subresource_selector.json, CMDObjectIndex))
        self.assertEqual(subresource_selector.json.name, "endpoint")
        self.assertTrue(isinstance(subresource_selector.json.prop, CMDArrayIndex))
        self.assertEqual(subresource_selector.json.prop.name, "properties.originGroups")
        self.assertEqual(len(subresource_selector.json.prop.identifiers), 1)
        identifier = subresource_selector.json.prop.identifiers[0]
        self.assertTrue(isinstance(identifier, CMDStringSchema))
        self.assertEqual(identifier.name, '[].name')
        self.assertEqual(identifier.arg, '$endpoint.properties.originGroups[].name')
        self.assertTrue(isinstance(subresource_selector.json.prop.item, CMDObjectIndexBase))
        self.assertEqual(subresource_selector.json.prop.item.additional_props, None)
        self.assertEqual(subresource_selector.json.prop.item.discriminator, None)
        self.assertTrue(isinstance(subresource_selector.json.prop.item.prop, CMDArrayIndex))
        self.assertEqual(subresource_selector.json.prop.item.prop.name, 'properties.origins')
        identifier = subresource_selector.json.prop.item.prop.identifiers[0]
        self.assertTrue(isinstance(identifier, CMDIntegerSchema))
        self.assertEqual(identifier.name, '[Index]')
        self.assertEqual(identifier.arg, '$endpoint.properties.originGroups[].properties.origins[Index]')
        self.assertTrue(isinstance(subresource_selector.json.prop.item.prop.item, CMDObjectIndexBase))
        self.assertEqual(subresource_selector.json.prop.item.prop.item.additional_props, None)
        self.assertEqual(subresource_selector.json.prop.item.prop.item.discriminator, None)

        self.assertEqual(len(delete_command.arg_groups), 1)
        args_var_set = set()
        for arg in delete_command.arg_groups[0].args:
            args_var_set.add(arg.var)
        self.assertEqual(args_var_set, {
            '$Path.endpointName', '$Path.profileName', '$Path.resourceGroupName', '$Path.subscriptionId',
            '$endpoint.properties.originGroups[].name',
            '$endpoint.properties.originGroups[].properties.origins[Index]'})

        instance_delete = None
        for op in delete_command.operations:
            if isinstance(op, CMDInstanceDeleteOperation):
                assert not instance_delete
                instance_delete = op.instance_delete
        self.assertTrue(isinstance(instance_delete, CMDJsonInstanceDeleteAction))
        self.assertEqual(instance_delete.ref, '$Subresource')
        self.assertEqual(delete_command.outputs, None)

        create_command = cfg.find_command("cdn", "profile", "endpoint", 'origin-group', 'origin', 'create')
        subresource_selector = create_command.subresource_selector
        self.assertTrue(isinstance(subresource_selector, CMDJsonSubresourceSelector))
        self.assertEqual(subresource_selector.ref, "$Instance")
        self.assertEqual(subresource_selector.var, "$Subresource")
        self.assertTrue(isinstance(subresource_selector.json, CMDObjectIndex))
        self.assertEqual(subresource_selector.json.name, "endpoint")
        self.assertTrue(isinstance(subresource_selector.json.prop, CMDArrayIndex))
        self.assertEqual(subresource_selector.json.prop.name, "properties.originGroups")
        self.assertEqual(len(subresource_selector.json.prop.identifiers), 1)
        identifier = subresource_selector.json.prop.identifiers[0]
        self.assertTrue(isinstance(identifier, CMDStringSchema))
        self.assertEqual(identifier.name, '[].name')
        self.assertEqual(identifier.arg, '$endpoint.properties.originGroups[].name')
        self.assertTrue(isinstance(subresource_selector.json.prop.item, CMDObjectIndexBase))
        self.assertEqual(subresource_selector.json.prop.item.additional_props, None)
        self.assertEqual(subresource_selector.json.prop.item.discriminator, None)
        self.assertTrue(isinstance(subresource_selector.json.prop.item.prop, CMDArrayIndex))
        self.assertEqual(subresource_selector.json.prop.item.prop.name, 'properties.origins')
        identifier = subresource_selector.json.prop.item.prop.identifiers[0]
        self.assertTrue(isinstance(identifier, CMDIntegerSchema))
        self.assertEqual(identifier.name, '[Index]')
        self.assertEqual(identifier.arg, '$endpoint.properties.originGroups[].properties.origins[Index]')
        self.assertTrue(isinstance(subresource_selector.json.prop.item.prop.item, CMDObjectIndexBase))
        self.assertEqual(subresource_selector.json.prop.item.prop.item.additional_props, None)
        self.assertEqual(subresource_selector.json.prop.item.prop.item.discriminator, None)

        self.assertEqual(len(create_command.arg_groups), 2)
        args_var_set = set()
        for arg_group in create_command.arg_groups:
            for arg in arg_group.args:
                args_var_set.add(arg.var)
                if arg.var == '$Path.endpointName':
                    self.assertEqual(arg.options, ['endpoint-name'])
                elif arg.var == '$endpoint.properties.originGroups[].properties.origins[Index]':
                    # create command will append item if index is not provided.
                    self.assertFalse(arg.required)
                    self.assertFalse(arg.nullable)
                elif arg.var == '$endpoint.properties.originGroups[].properties.origins[].id':
                    self.assertFalse(arg.required)
                    self.assertFalse(arg.nullable)

        self.assertEqual(args_var_set, {
            '$Path.endpointName', '$Path.profileName', '$Path.resourceGroupName', '$Path.subscriptionId',
            '$endpoint.properties.originGroups[].name',
            '$endpoint.properties.originGroups[].properties.origins[Index]',
            '$endpoint.properties.originGroups[].properties.origins[].id'})
        instance_create = None
        for op in create_command.operations:
            if isinstance(op, CMDInstanceCreateOperation):
                assert not instance_create
                instance_create = op.instance_create
        self.assertTrue(isinstance(instance_create, CMDJsonInstanceCreateAction))
        self.assertEqual(instance_create.ref, '$Subresource')
        self.assertEqual(instance_create.json.schema.name, 'endpoint.properties.originGroups[].properties.origins[]')
        self.assertEqual(create_command.outputs[0].ref, '$Subresource')

        update_command = cfg.find_command("cdn", "profile", "endpoint", 'origin-group', 'origin', 'update')
        subresource_selector = update_command.subresource_selector
        subresource_selector = create_command.subresource_selector
        self.assertTrue(isinstance(subresource_selector, CMDJsonSubresourceSelector))
        self.assertEqual(subresource_selector.ref, "$Instance")
        self.assertEqual(subresource_selector.var, "$Subresource")
        self.assertTrue(isinstance(subresource_selector.json, CMDObjectIndex))
        self.assertEqual(subresource_selector.json.name, "endpoint")
        self.assertTrue(isinstance(subresource_selector.json.prop, CMDArrayIndex))
        self.assertEqual(subresource_selector.json.prop.name, "properties.originGroups")
        self.assertEqual(len(subresource_selector.json.prop.identifiers), 1)
        identifier = subresource_selector.json.prop.identifiers[0]
        self.assertTrue(isinstance(identifier, CMDStringSchema))
        self.assertEqual(identifier.name, '[].name')
        self.assertEqual(identifier.arg, '$endpoint.properties.originGroups[].name')
        self.assertTrue(isinstance(subresource_selector.json.prop.item, CMDObjectIndexBase))
        self.assertEqual(subresource_selector.json.prop.item.additional_props, None)
        self.assertEqual(subresource_selector.json.prop.item.discriminator, None)
        self.assertTrue(isinstance(subresource_selector.json.prop.item.prop, CMDArrayIndex))
        self.assertEqual(subresource_selector.json.prop.item.prop.name, 'properties.origins')
        identifier = subresource_selector.json.prop.item.prop.identifiers[0]
        self.assertTrue(isinstance(identifier, CMDIntegerSchema))
        self.assertEqual(identifier.name, '[Index]')
        self.assertEqual(identifier.arg, '$endpoint.properties.originGroups[].properties.origins[Index]')
        self.assertTrue(isinstance(subresource_selector.json.prop.item.prop.item, CMDObjectIndexBase))
        self.assertEqual(subresource_selector.json.prop.item.prop.item.additional_props, None)
        self.assertEqual(subresource_selector.json.prop.item.prop.item.discriminator, None)

        self.assertEqual(len(update_command.arg_groups), 2)
        args_var_set = set()
        for arg_group in update_command.arg_groups:
            for arg in arg_group.args:
                args_var_set.add(arg.var)
                if arg.var == '$Path.endpointName':
                    self.assertEqual(arg.options, ['endpoint-name'])
                elif arg.var == '$endpoint.properties.originGroups[].properties.origins[Index]':
                    self.assertTrue(arg.required)
                    self.assertFalse(arg.nullable)
                elif arg.var == '$endpoint.properties.originGroups[].properties.origins[].id':
                    self.assertFalse(arg.required)
                    self.assertTrue(arg.nullable)

        self.assertEqual(args_var_set, {
            '$Path.endpointName', '$Path.profileName', '$Path.resourceGroupName', '$Path.subscriptionId',
            '$endpoint.properties.originGroups[].name',
            '$endpoint.properties.originGroups[].properties.origins[Index]',
            '$endpoint.properties.originGroups[].properties.origins[].id'})
        instance_update = None
        for op in update_command.operations:
            if isinstance(op, CMDInstanceUpdateOperation):
                assert not instance_update
                instance_update = op.instance_update
        self.assertTrue(isinstance(instance_update, CMDJsonInstanceUpdateAction))
        self.assertEqual(instance_update.ref, '$Subresource')
        self.assertEqual(instance_create.json.schema.name, 'endpoint.properties.originGroups[].properties.origins[]')
        self.assertEqual(update_command.outputs[0].ref, '$Subresource')
