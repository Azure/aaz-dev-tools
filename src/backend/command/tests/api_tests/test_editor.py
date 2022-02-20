import json
import os

from utils.stage import AAZStageEnum
from command.controller.workspace_cfg_editor import WorkspaceCfgEditor
from command.controller.workspace_manager import WorkspaceManager
from command.tests.common import CommandTestCase, workspace_name
from swagger.utils.tools import swagger_resource_path_to_resource_id
from utils.plane import PlaneEnum


class APIEditorTest(CommandTestCase):

    @workspace_name("test_workspaces_1", arg_name="name1")
    @workspace_name("test_workspaces_2", arg_name="name2")
    def test_workspaces(self, name1, name2):
        with self.app.test_client() as c:
            rv = c.post(f"/AAZ/Editor/Workspaces", json={
                "name": name1,
                "plane": PlaneEnum.Mgmt,
            })
            assert rv.status_code == 200
            ws1 = rv.get_json()
            assert ws1['name'] == name1
            assert ws1['plane'] == PlaneEnum.Mgmt
            assert ws1['version']
            assert ws1['url']
            assert ws1['commandTree']['names'] == ['aaz']
            assert os.path.exists(ws1['folder'])

            rv = c.post(f"/AAZ/Editor/Workspaces", json={
                "name": name2,
                "plane": PlaneEnum.Mgmt,
            })
            assert rv.status_code == 200
            ws2 = rv.get_json()
            assert ws2['name'] == name2
            assert ws2['plane'] == PlaneEnum.Mgmt
            assert ws2['version']
            assert ws2['url']
            assert os.path.exists(ws2['folder'])

            rv = c.get(f"/AAZ/Editor/Workspaces")
            ws_list = rv.get_json()
            assert len(ws_list) == 2
            for ws_data in ws_list:
                if ws_data['name'] == name1:
                    assert ws_data['url'] == ws1['url']
                    assert ws_data['folder'] == ws1['folder']
                elif ws_data['name'] == name2:
                    assert ws_data['url'] == ws2['url']
                    assert ws_data['folder'] == ws2['folder']

            rv = c.post(f"/AAZ/Editor/Workspaces", json={
                "name": name2,
                "plane": PlaneEnum.Mgmt,
            })
            assert rv.status_code == 409

    @workspace_name("test_workspace_1")
    def test_workspace(self, ws_name):
        with self.app.test_client() as c:
            rv = c.post(f"/AAZ/Editor/Workspaces", json={
                "name": ws_name,
                "plane": PlaneEnum.Mgmt,
            })
            assert rv.status_code == 200
            ws = rv.get_json()

            rv = c.get(ws['url'])
            assert rv.status_code == 200
            assert rv.get_json() == ws
            rv = c.get(f"/AAZ/Editor/Workspaces/{ws['name']}")
            assert rv.status_code == 200
            assert rv.get_json() == ws

            rv = c.delete(ws['url'])
            assert rv.status_code == 200
            rv = c.delete(ws['url'])
            assert rv.status_code == 204

    @workspace_name("test_workspace_add_swagger")
    def test_workspace_add_swagger(self, ws_name):
        with self.app.test_client() as c:
            rv = c.post(f"/AAZ/Editor/Workspaces", json={
                "name": ws_name,
                "plane": PlaneEnum.Mgmt,
            })
            assert rv.status_code == 200
            ws = rv.get_json()
            ws_url = ws['url']

            rv = c.get(f"{ws_url}/CommandTree/Nodes/aaz")
            assert rv.status_code == 200
            node = rv.get_json()
            assert node['names'] == ['aaz']

            rv = c.post(f"{ws_url}/CommandTree/Nodes/aaz/AddSwagger", json={
                'module': 'edgeorder',
                'version': '2021-12-01',
                'resources': [
                    swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/providers/Microsoft.EdgeOrder/addresses'),
                    swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.EdgeOrder/addresses'),
                    swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.EdgeOrder/addresses/{addressName}'),
                ]
            })
            assert rv.status_code == 200

            rv = c.get(f"{ws_url}/CommandTree/Nodes/aaz")
            assert rv.status_code == 200
            node = rv.get_json()
            cg = node['commandGroups']
            assert len(cg) == 1 and 'edge-order' in cg
            assert cg['edge-order']['names'] == ['edge-order']
            cg = cg['edge-order']['commandGroups']
            assert len(cg) == 1 and 'address' in cg
            assert cg['address']['names'] == ['edge-order', 'address']
            commands = cg['address']['commands']
            assert len(commands) == 5 and set(commands.keys()) == {'create', 'delete', 'list', 'show', 'update'}
            for cmd_name in ('create', 'delete', 'show', 'update'):
                assert len(commands[cmd_name]['resources']) == 1
                assert commands[cmd_name]['resources'][0]['version'] == '2021-12-01'
                assert commands[cmd_name]['resources'][0]['id'] == swagger_resource_path_to_resource_id(
                    '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.EdgeOrder/addresses/{addressName}')
            assert len(commands['list']['resources']) == 2
            assert commands['list']['resources'][0]['id'] == swagger_resource_path_to_resource_id(
                '/subscriptions/{subscriptionId}/providers/Microsoft.EdgeOrder/addresses')
            assert commands['list']['resources'][0]['version'] == '2021-12-01'
            assert commands['list']['resources'][1]['id'] == swagger_resource_path_to_resource_id(
                '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.EdgeOrder/addresses')
            assert commands['list']['resources'][1]['version'] == '2021-12-01'

            rv = c.get(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/address/Leaves/list")
            assert rv.status_code == 200
            command = rv.get_json()
            assert command['names'] == ['edge-order', 'address', 'list']
            assert len(command['conditions']) == 2
            assert len(command['argGroups']) == 1
            assert len(command['argGroups'][0]['args']) == 4
            assert len(command['operations']) == 2
            assert len(command['outputs']) == 1
            assert len(command['resources']) == 2
            assert command['version'] == '2021-12-01'

            rv = c.get(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/address/Leaves/show")
            assert rv.status_code == 200
            command = rv.get_json()
            assert command['names'] == ['edge-order', 'address', 'show']
            assert len(command['argGroups']) == 1
            assert 'conditions' not in command
            assert len(command['operations']) == 1
            assert len(command['outputs']) == 1
            assert len(command['resources']) == 1
            assert command['version'] == '2021-12-01'

            rv = c.get(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/address/Leaves/delete")
            assert rv.status_code == 200
            command = rv.get_json()
            assert command['names'] == ['edge-order', 'address', 'delete']
            assert len(command['argGroups']) == 1
            assert 'conditions' not in command
            assert len(command['operations']) == 1
            assert 'outputs' not in command
            assert len(command['resources']) == 1
            assert command['version'] == '2021-12-01'

            rv = c.get(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/address/Leaves/create")
            assert rv.status_code == 200
            command = rv.get_json()
            assert command['names'] == ['edge-order', 'address', 'create']
            assert len(command['argGroups']) == 1
            assert 'conditions' not in command
            assert len(command['operations']) == 1
            assert len(command['outputs']) == 1
            assert len(command['resources']) == 1
            assert command['version'] == '2021-12-01'

            rv = c.get(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/address/Leaves/update")
            assert rv.status_code == 200
            command = rv.get_json()
            assert command['names'] == ['edge-order', 'address', 'update']
            assert len(command['argGroups']) == 2
            assert 'conditions' not in command
            assert len(command['operations']) == 4  # Get, InstanceUpdate, GenericUpdate, Put
            assert len(command['outputs']) == 1
            assert len(command['resources']) == 1
            assert command['version'] == '2021-12-01'

    @workspace_name("test_workspace_command_tree_update")
    def test_workspace_command_tree_update(self, ws_name):
        with self.app.test_client() as c:
            rv = c.post(f"/AAZ/Editor/Workspaces", json={
                "name": ws_name,
                "plane": PlaneEnum.Mgmt,
            })
            self.assertTrue(rv.status_code == 200)
            ws = rv.get_json()
            ws_url = ws['url']

            rv = c.post(f"{ws_url}/CommandTree/Nodes/aaz/AddSwagger", json={
                'module': 'edgeorder',
                'version': '2021-12-01',
                'resources': [
                    swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/providers/Microsoft.EdgeOrder/addresses'),
                    swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/providers/Microsoft.EdgeOrder/listProductFamilies'),
                    swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/providers/Microsoft.EdgeOrder/listConfigurations'),
                    swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/providers/Microsoft.EdgeOrder/productFamiliesMetadata'),
                    swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/providers/Microsoft.EdgeOrder/orders'),
                    swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/providers/Microsoft.EdgeOrder/orderItems'),
                    swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.EdgeOrder/addresses'),
                    swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.EdgeOrder/addresses/{addressName}'),
                    swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.EdgeOrder/orders'),
                    swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.EdgeOrder/locations/{location}/orders/{orderName}'),
                    swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.EdgeOrder/orderItems'),
                    swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.EdgeOrder/orderItems/{orderItemName}'),
                    swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.EdgeOrder/orderItems/{orderItemName}/cancel'),
                    swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.EdgeOrder/orderItems/{orderItemName}/return'),
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.get(f"{ws_url}/CommandTree/Nodes/aaz")
            self.assertTrue(rv.status_code == 200)
            command_tree = rv.get_json()

            rv = c.get(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/Leaves/list-product-family")
            self.assertTrue(rv.status_code == 200)
            command = rv.get_json()
            rv = c.post(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/Leaves/list-product-family/Rename", json={
                'name': "edge-order product-family list"
            })
            self.assertTrue(rv.status_code == 200)
            command = rv.get_json()
            self.assertTrue(command['names'] == ['edge-order', 'product-family', 'list'])
            rv = c.get(f"{ws_url}/CommandTree/Nodes/aaz/edge-order")
            self.assertTrue(rv.status_code == 200)
            edge_order_node = rv.get_json()
            self.assertTrue('product-family' in edge_order_node['commandGroups'])
            product_family_node = edge_order_node['commandGroups']['product-family']
            self.assertTrue(product_family_node['names'] == ['edge-order', 'product-family'])
            self.assertTrue('list' in product_family_node['commands'])
            list_leaf = product_family_node['commands']['list']
            self.assertTrue(list_leaf['names'] == ['edge-order', 'product-family', 'list'])

            rv = c.get(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/product-family/Leaves/list")
            self.assertTrue(rv.status_code == 200)
            command = rv.get_json()
            self.assertTrue(command['names'] == ['edge-order', 'product-family', 'list'])
            self.assertTrue(command['resources'][0]['id'] == swagger_resource_path_to_resource_id(
                '/subscriptions/{subscriptionId}/providers/Microsoft.EdgeOrder/listProductFamilies'))

            rv = c.post(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/Leaves/product-families-metadatum/Rename", json={
                'name': "edge-order product-family list-metadata"
            })
            self.assertTrue(rv.status_code == 200)
            command = rv.get_json()
            self.assertTrue(command['names'] == ['edge-order', 'product-family', 'list-metadata'])

            rv = c.post(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/order-item/Rename", json={
                'name': "edge-order order item"
            })
            self.assertTrue(rv.status_code == 200)
            order_item_node = rv.get_json()
            self.assertTrue(order_item_node["names"] == ['edge-order', 'order', 'item'])

            rv = c.get(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/order")
            self.assertTrue(rv.status_code == 200)
            order_node = rv.get_json()
            self.assertTrue(order_node["names"] == ['edge-order', 'order'])
            self.assertTrue(len(order_node["commands"]) == 2)
            self.assertTrue(len(order_node["commandGroups"]) == 1)
            order_item_node = order_node["commandGroups"]['item']
            self.assertTrue(len(order_item_node['commands']) == 7)

            rv = c.post(f"{ws_url}/CommandTree/Nodes/aaz/edge-order", json={
                "name": "product item"
            })
            self.assertTrue(rv.status_code == 200)
            product_item_node = rv.get_json()
            self.assertTrue(product_item_node["names"] == ["edge-order", "product", "item"])
            rv = c.delete(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/order")
            self.assertTrue(rv.status_code == 409)
            rv = c.delete(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/product")
            self.assertTrue(rv.status_code == 200)
            rv = c.delete(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/product/item")
            self.assertTrue(rv.status_code == 204)

            rv = c.get(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/Resources")
            self.assertTrue(rv.status_code == 200)
            data = rv.get_json()
            self.assertTrue(len(data) == 14)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/order/item", json={
                "help": {
                    "short": "This is a short help",
                },
                "stage": AAZStageEnum.Preview,
            })
            self.assertTrue(rv.status_code == 200)
            data = rv.get_json()
            self.assertTrue(data['names'] == ["edge-order", "order", "item"])
            self.assertTrue(data['help']['short'] == "This is a short help")
            self.assertTrue(data['stage'] == AAZStageEnum.Preview)
            self.assertTrue(data['commands']['create']['stage'] == AAZStageEnum.Preview)

            rv = c.get(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/order/item/Leaves/create")
            self.assertTrue(rv.status_code == 200)
            data = rv.get_json()
            self.assertTrue(data['names'] == ['edge-order', 'order', 'item', 'create'])
            self.assertTrue(data['stage'] == AAZStageEnum.Preview)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/order/item/Leaves/create", json={
                "help": {
                    "short": "This is command help",
                    "lines": [
                        "help line 1",
                        "help line 2"
                    ]
                },
                "stage": AAZStageEnum.Experimental,
                "examples": [
                    {
                        "name": "create edge order item",
                        "commands": [
                            "edge-order order item create -g {}"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)
            data = rv.get_json()
            self.assertTrue(data['stage'] == AAZStageEnum.Experimental)
            self.assertTrue(data['help']['short'] == "This is command help")
            self.assertTrue(data['help']['lines'] == ["help line 1", "help line 2"])
            self.assertTrue(data['examples'] == [
                {
                    "name": "create edge order item",
                    "commands": [
                        "edge-order order item create -g {}"
                    ]
                }
            ])

            rv = c.get(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/order/item")
            self.assertTrue(rv.status_code == 200)
            data = rv.get_json()
            self.assertTrue(data['commands']['create']['stage'] == AAZStageEnum.Experimental)

    @workspace_name("test_workspace_command_merge")
    def test_workspace_command_merge(self, ws_name):
        with self.app.test_client() as c:
            rv = c.post(f"/AAZ/Editor/Workspaces", json={
                "name": ws_name,
                "plane": PlaneEnum.Mgmt,
            })
            self.assertTrue(rv.status_code == 200)
            ws = rv.get_json()
            ws_url = ws['url']

            rv = c.post(f"{ws_url}/CommandTree/Nodes/aaz/AddSwagger", json={
                'module': 'edgeorder',
                'version': '2021-12-01',
                'resources': [
                    swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/providers/Microsoft.EdgeOrder/addresses'),
                ]
            })
            self.assertTrue(rv.status_code == 200)
            rv = c.get(f"{ws_url}/CommandTree/Nodes/aaz/edge-order")
            self.assertTrue(rv.status_code == 200)
            data = rv.get_json()

            rv = c.post(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/address/Leaves/list/Rename", json={
                'name': "edge-order address list-1"
            })
            self.assertTrue(rv.status_code == 200)
            rv = c.get(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/address")
            self.assertTrue(rv.status_code == 200)
            data = rv.get_json()
            self.assertTrue(data['commands']['list-1']['names'] == ['edge-order', 'address', 'list-1'])

            rv = c.post(f"{ws_url}/CommandTree/Nodes/aaz/AddSwagger", json={
                'module': 'edgeorder',
                'version': '2021-12-01',
                'resources': [
                    swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.EdgeOrder/addresses'),
                ]
            })
            self.assertTrue(rv.status_code == 200)
            rv = c.get(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/address")
            self.assertTrue(rv.status_code == 200)
            data = rv.get_json()
            self.assertTrue(len(data['commands']) == 2 and 'list' in data['commands'] and 'list-1' in data['commands'])

            rv = c.post(f"{ws_url}/Resources/Merge", json={
                "mainResource": {
                    "id": swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.EdgeOrder/addresses'),
                    "version": '2021-12-01'
                },
                "plusResource": {
                    "id": swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/providers/Microsoft.EdgeOrder/addresses'),
                    "version": '2021-12-01'
                }
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.get(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/address")
            self.assertTrue(rv.status_code == 200)
            data = rv.get_json()
            self.assertTrue(len(data['commands']) == 1 and 'list' in data['commands'] and len(data['commands']['list']['resources']) == 2)

            manager = WorkspaceManager(name=ws_name)
            path_main = WorkspaceCfgEditor.get_cfg_path(
                manager.folder,
                swagger_resource_path_to_resource_id(
                    '/subscriptions/{subscriptionId}/providers/Microsoft.EdgeOrder/addresses'),
            )
            with open(path_main, 'r') as f:
                data = json.load(f)
                self.assertTrue("$ref" not in data)
            path_plus = WorkspaceCfgEditor.get_cfg_path(
                manager.folder,
                swagger_resource_path_to_resource_id(
                    '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.EdgeOrder/addresses')
            )
            with open(path_plus, 'r') as f:
                data = json.load(f)
                self.assertTrue("$ref" in data)

    @workspace_name("test_workspace_aaz_generate")
    def test_workspace_aaz_generate(self, ws_name):
        with self.app.test_client() as c:
            rv = c.post(f"/AAZ/Editor/Workspaces", json={
                "name": ws_name,
                "plane": PlaneEnum.Mgmt,
            })
            self.assertTrue(rv.status_code == 200)
            ws = rv.get_json()
            ws_url = ws['url']
            rv = c.post(f"{ws_url}/CommandTree/Nodes/aaz/AddSwagger", json={
                'module': 'edgeorder',
                'version': '2021-12-01',
                'resources': [
                    swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/providers/Microsoft.EdgeOrder/addresses'),
                    swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/providers/Microsoft.EdgeOrder/listProductFamilies'),
                    swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/providers/Microsoft.EdgeOrder/listConfigurations'),
                    swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/providers/Microsoft.EdgeOrder/productFamiliesMetadata'),
                    swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/providers/Microsoft.EdgeOrder/orders'),
                    swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/providers/Microsoft.EdgeOrder/orderItems'),
                    swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.EdgeOrder/addresses'),
                    swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.EdgeOrder/addresses/{addressName}'),
                    swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.EdgeOrder/orders'),
                    swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.EdgeOrder/locations/{location}/orders/{orderName}'),
                    swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.EdgeOrder/orderItems'),
                    swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.EdgeOrder/orderItems/{orderItemName}'),
                    swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.EdgeOrder/orderItems/{orderItemName}/cancel'),
                    swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.EdgeOrder/orderItems/{orderItemName}/return'),
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.post(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/Leaves/list-product-family/Rename", json={
                'name': "edge-order product-family list"
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.post(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/Leaves/product-families-metadatum/Rename", json={
                'name': "edge-order product-family list-metadata"
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.post(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/order-item/Rename", json={
                'name': "edge-order order item"
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.get(f"{ws_url}/CommandTree/Nodes/aaz")
            self.assertTrue(rv.status_code == 200)
            command_tree = rv.get_json()

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/edge-order", json={
                "help": {
                    "short": "Manage edge order.",
                },
                "stage": AAZStageEnum.Preview
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/address", json={
                "help": {
                    "short": "Manage the address of edge order.",
                },
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/order", json={
                "help": {
                    "short": "Manage the order of edge order.",
                },
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/product-family", json={
                "help": {
                    "short": "Manage the product family of edge order.",
                },
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/order/item", json={
                "help": {
                    "short": "Manage the order item of edge order.",
                },
                "stage": AAZStageEnum.Preview
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/Leaves/list-configuration", json={
                "help": {
                    "short": "List the configuration of the edge order.",
                    "lines": [
                        "Provides the list of configurations for the given product family, product line and product.",
                    ]
                },
                "stage": AAZStageEnum.Experimental
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/address/Leaves/list", json={
                "help": {
                    "short": "List the addresses of the edge order.",
                },
                "stage": AAZStageEnum.Experimental
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/order/Leaves/list", json={
                "help": {
                    "short": "List the orders of the edge order.",
                },
                "stage": AAZStageEnum.Experimental
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/product-family/Leaves/list", json={
                "help": {
                    "short": "List the product families of the edge order.",
                },
                "stage": AAZStageEnum.Experimental
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/product-family/Leaves/list-metadata", json={
                "help": {
                    "short": "List the product families metadata of the edge order.",
                },
                "stage": AAZStageEnum.Experimental
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/order/item/Leaves/list", json={
                "help": {
                    "short": "List order item of edge order.",
                },
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.post(f"{ws_url}/Generate")
            self.assertTrue(rv.status_code == 200)

    @workspace_name("test_workspace_command_node_rename")
    def test_workspace_command_node_rename(self, ws_name):
        with self.app.test_client() as c:
            rv = c.post(f"/AAZ/Editor/Workspaces", json={
                "name": ws_name,
                "plane": PlaneEnum.Mgmt,
            })
            self.assertTrue(rv.status_code == 200)
            ws = rv.get_json()
            ws_url = ws['url']

            rv = c.post(f"{ws_url}/CommandTree/Nodes/aaz/AddSwagger", json={
                'module': 'edgeorder',
                'version': '2021-12-01',
                'resources': [
                    swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/providers/Microsoft.EdgeOrder/addresses'),
                    swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/providers/Microsoft.EdgeOrder/listProductFamilies'),
                    swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/providers/Microsoft.EdgeOrder/listConfigurations'),
                    swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/providers/Microsoft.EdgeOrder/productFamiliesMetadata'),
                    swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/providers/Microsoft.EdgeOrder/orders'),
                    swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/providers/Microsoft.EdgeOrder/orderItems'),
                    swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.EdgeOrder/addresses'),
                    swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.EdgeOrder/addresses/{addressName}'),
                    swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.EdgeOrder/orders'),
                    swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.EdgeOrder/locations/{location}/orders/{orderName}'),
                    swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.EdgeOrder/orderItems'),
                    swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.EdgeOrder/orderItems/{orderItemName}'),
                    swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.EdgeOrder/orderItems/{orderItemName}/cancel'),
                    swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.EdgeOrder/orderItems/{orderItemName}/return'),
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.get(f"{ws_url}/CommandTree/Nodes/aaz")
            self.assertTrue(rv.status_code == 200)
            command_tree = rv.get_json()

            rv = c.post(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/order-item/Rename", json={
                'name': "order-item"
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.get(f"{ws_url}/CommandTree/Nodes/aaz")
            self.assertTrue(rv.status_code == 200)
            command_tree = rv.get_json()
            self.assertTrue(command_tree['commandGroups']['order-item']['names'] == ['order-item'])

    @workspace_name("test_workspace_aaz_generate_for_operation_api")
    def test_workspace_aaz_generate_for_operation_api(self, ws_name):
        with self.app.test_client() as c:
            rv = c.post(f"/AAZ/Editor/Workspaces", json={
                "name": ws_name,
                "plane": PlaneEnum.Mgmt,
            })
            self.assertTrue(rv.status_code == 200)
            ws = rv.get_json()
            ws_url = ws['url']
            rv = c.post(f"{ws_url}/CommandTree/Nodes/aaz/AddSwagger", json={
                'module': 'edgeorder',
                'version': '2021-12-01',
                'resources': [
                    swagger_resource_path_to_resource_id(
                        '/providers/Microsoft.EdgeOrder/operations'),
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.get(f"{ws_url}/CommandTree/Nodes/aaz")
            self.assertTrue(rv.status_code == 200)
            command_tree = rv.get_json()

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/edge-order", json={
                "help": {
                    "short": "Manage edge order.",
                },
                "stage": AAZStageEnum.Preview
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/operation", json={
                "help": {
                    "short": "Manage edge order.",
                },
                "stage": AAZStageEnum.Preview
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/operation/Leaves/list", json={
                "help": {
                    "short": "Manage edge order.",
                },
                "stage": AAZStageEnum.Preview
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.post(f"{ws_url}/Generate")
            self.assertTrue(rv.status_code == 200)
