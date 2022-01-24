from command.controller.workspace_manager import WorkspaceManager
from command.controller.workspace_cfg_editor import WorkspaceCfgEditor
from command.tests.common import CommandTestCase
from utils.plane import PlaneEnum
import os
import json
from utils import exceptions
from swagger.utils.tools import swagger_resource_path_to_resource_id


def workspace_name(suffix):
    def decorator(func):
        def wrapper(self, **kwargs):
            name = f"{self.__class__.__name__}_{func.__name__}_{suffix}"
            return func(self, **kwargs, name=name)
        return wrapper
    return decorator


class WorkspaceManagerTest(CommandTestCase):

    @workspace_name("1")
    def test_workspace_manager(self, name):
        manager = WorkspaceManager(name)
        assert manager.path.endswith(os.path.join(name, "ws.json"))

        manager = WorkspaceManager.new(name, plane=PlaneEnum.Mgmt)
        manager.save()
        assert os.path.exists(manager.path)
        with open(manager.path, 'r') as f:
            data = json.load(f)
        assert data['name'] == name
        assert data['plane'] == PlaneEnum.Mgmt
        assert data['version']
        assert data['commandTree'] == {
            "name": WorkspaceManager.COMMAND_TREE_ROOT_NAME
        }

        manager_2 = WorkspaceManager(name)
        manager_2.load()
        assert manager_2.ws.name == name
        assert manager_2.ws.plane == PlaneEnum.Mgmt
        assert manager_2.ws.version == manager.ws.version
        assert manager_2.ws.command_tree.name == WorkspaceManager.COMMAND_TREE_ROOT_NAME
        manager_2.save()

        with self.assertRaises(exceptions.InvalidAPIUsage):
            manager.save()


class WorkspaceEditorTest(CommandTestCase):

    @workspace_name("1")
    def test_workspace_editor_add_resources_by_swagger(self, name):
        manager = WorkspaceManager.new(name, plane=PlaneEnum.Mgmt)
        manager.save()

        mod_names = "edgeorder"

        manager.add_new_resources_by_swagger(
            mod_names=mod_names,
            version='2021-12-01',
            resource_ids=[
                swagger_resource_path_to_resource_id('/subscriptions/{subscriptionId}/providers/Microsoft.EdgeOrder/addresses'),
                swagger_resource_path_to_resource_id('/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.EdgeOrder/addresses'),
                swagger_resource_path_to_resource_id('/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.EdgeOrder/addresses/{addressName}'),
            ]
        )
        manager.save()

        manager = WorkspaceManager(name)
        manager.load()
        assert 'edge-order' in manager.ws.command_tree.command_groups
        assert 'address' in manager.ws.command_tree.command_groups['edge-order'].command_groups
        address_cg = manager.ws.command_tree.command_groups['edge-order'].command_groups['address']
        assert 'list' in address_cg.commands
        assert 'create' in address_cg.commands
        assert 'show' in address_cg.commands
        assert 'delete' in address_cg.commands
        assert 'update' in address_cg.commands

        assert manager.load_cfg_editor_by_command(address_cg.commands['list'])
        assert manager.load_cfg_editor_by_command(address_cg.commands['create'])
        assert manager.load_cfg_editor_by_command(address_cg.commands['show'])
        assert manager.load_cfg_editor_by_command(address_cg.commands['delete'])
        assert manager.load_cfg_editor_by_command(address_cg.commands['update'])
