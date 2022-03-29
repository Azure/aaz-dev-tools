import json
import os

from command.controller.workspace_cfg_editor import WorkspaceCfgEditor
from command.controller.workspace_manager import WorkspaceManager
from command.tests.common import CommandTestCase, workspace_name
from swagger.utils.tools import swagger_resource_path_to_resource_id
from utils.base64 import b64encode_str
from utils.plane import PlaneEnum
from utils.stage import AAZStageEnum


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
                    {'id': swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/providers/Microsoft.EdgeOrder/addresses')},
                    {'id': swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.EdgeOrder/addresses')},
                    {'id': swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.EdgeOrder/addresses/{addressName}')},
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
            assert len(command['argGroups']) == 2
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
            assert len(command['operations']) == 3  # Get, InstanceUpdate, Put
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
                    {'id': swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/providers/Microsoft.EdgeOrder/addresses')},
                    {'id': swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/providers/Microsoft.EdgeOrder/listConfigurations')},
                    {'id': swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/providers/Microsoft.EdgeOrder/orders')},
                    {'id': swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/providers/Microsoft.EdgeOrder/orderItems')},
                    {'id': swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.EdgeOrder/addresses')},
                    {'id': swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.EdgeOrder/addresses/{addressName}')},
                    {'id': swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.EdgeOrder/orders')},
                    {'id': swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.EdgeOrder/locations/{location}/orders/{orderName}')},
                    {'id': swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.EdgeOrder/orderItems')},
                    {'id': swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.EdgeOrder/orderItems/{orderItemName}')},
                    {'id': swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.EdgeOrder/orderItems/{orderItemName}/cancel')},
                    {'id': swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.EdgeOrder/orderItems/{orderItemName}/return')},
                    {'id': swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/providers/Microsoft.EdgeOrder/productFamiliesMetadata')},
                    {'id': swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/providers/Microsoft.EdgeOrder/listProductFamilies')},
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

            # try delete resource with CRUD
            resource = data['commands']['create']['resources'][0]
            resource_id = resource['id']
            resource_version = resource['version']

            rv = c.get(f"{ws_url}/Resources/{b64encode_str(resource_id)}/V/{b64encode_str(resource_version)}/Commands")
            self.assertTrue(rv.status_code == 200)
            data = rv.get_json()
            self.assertTrue(len(data) == 4)
            for cmd in data:
                self.assertTrue(cmd['names'][:-1] == ["edge-order", "order", "item"])

            rv = c.delete(f"{ws_url}/Resources/{b64encode_str(resource_id)}/V/{b64encode_str(resource_version)}")
            self.assertTrue(rv.status_code == 200)

            rv = c.get(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/order/item")
            self.assertTrue(rv.status_code == 200)
            data = rv.get_json()
            self.assertTrue(
                'create' not in data['commands'] and 'show' not in data['commands'] and 'update' not in data[
                    'commands'] and 'delete' not in data['commands'])

            # try delete one resource in list
            self.assertTrue(len(data['commands']['list']['resources']) > 1)
            resource = data['commands']['list']['resources'][0]
            resource_id = resource['id']
            resource_version = resource['version']

            rv = c.delete(f"{ws_url}/Resources/{b64encode_str(resource_id)}/V/{b64encode_str(resource_version)}")
            self.assertTrue(rv.status_code == 200)

            rv = c.get(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/order/item")
            self.assertTrue(rv.status_code == 200)
            data = rv.get_json()
            self.assertTrue('list' not in data['commands'])

    @workspace_name("test_list_merge")
    def test_list_merge(self, ws_name):
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
                    {'id': swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/providers/Microsoft.EdgeOrder/addresses')},
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.post(f"{ws_url}/CommandTree/Nodes/aaz/AddSwagger", json={
                'module': 'edgeorder',
                'version': '2021-12-01',
                'resources': [
                    {'id': swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.EdgeOrder/addresses')},
                ]
            })
            self.assertTrue(rv.status_code == 200)
            rv = c.get(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/address")
            self.assertTrue(rv.status_code == 200)
            data = rv.get_json()
            self.assertTrue(len(data['commands']) == 1 and 'list' in data['commands'])

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
                    {'id': swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/providers/Microsoft.EdgeOrder/addresses')},
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
                    {'id': swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.EdgeOrder/addresses')},
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
            self.assertTrue(len(data['commands']) == 1 and 'list' in data['commands'] and len(
                data['commands']['list']['resources']) == 2)

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

    @workspace_name("test_workspace_aaz_generate_edge_order")
    def test_workspace_aaz_generate_edge_order(self, ws_name):
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
                    {'id': swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/providers/Microsoft.EdgeOrder/addresses')},
                    {'id': swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/providers/Microsoft.EdgeOrder/listProductFamilies')},
                    {'id': swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/providers/Microsoft.EdgeOrder/listConfigurations')},
                    {'id': swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/providers/Microsoft.EdgeOrder/productFamiliesMetadata')},
                    {'id': swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/providers/Microsoft.EdgeOrder/orders')},
                    {'id': swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/providers/Microsoft.EdgeOrder/orderItems')},
                    {'id': swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.EdgeOrder/addresses')},
                    {'id': swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.EdgeOrder/addresses/{addressName}')},
                    {'id': swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.EdgeOrder/orders')},
                    {'id': swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.EdgeOrder/locations/{location}/orders/{orderName}')},
                    {'id': swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.EdgeOrder/orderItems')},
                    {'id': swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.EdgeOrder/orderItems/{orderItemName}')},
                    {'id': swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.EdgeOrder/orderItems/{orderItemName}/cancel')},
                    {'id': swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.EdgeOrder/orderItems/{orderItemName}/return')},
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

    @workspace_name("test_workspace_aaz_generate_databricks")
    def test_workspace_aaz_generate_databricks(self, ws_name):
        with self.app.test_client() as c:
            rv = c.post(f"/AAZ/Editor/Workspaces", json={
                "name": ws_name,
                "plane": PlaneEnum.Mgmt,
            })
            self.assertTrue(rv.status_code == 200)
            ws = rv.get_json()
            ws_url = ws['url']
            rv = c.post(f"{ws_url}/CommandTree/Nodes/aaz/AddSwagger", json={
                'module': 'databricks',
                'version': '2018-04-01',
                'resources': [
                    {'id': swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Databricks/workspaces/{workspaceName}')},
                    {'id': swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Databricks/workspaces')},
                    {'id': swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/providers/Microsoft.Databricks/workspaces')},
                    {'id': swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Databricks/workspaces/{workspaceName}/virtualNetworkPeerings/{peeringName}')},
                    {'id': swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Databricks/workspaces/{workspaceName}/virtualNetworkPeerings')},
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.post(f"{ws_url}/CommandTree/Nodes/aaz/databricks/workspace/virtual-network-peering/Rename", json={
                'name': "databricks workspace vnet-peering"
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.get(f"{ws_url}/CommandTree/Nodes/aaz")
            self.assertTrue(rv.status_code == 200)
            command_tree = rv.get_json()

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/databricks", json={
                "help": {
                    "short": "Manage databricks workspaces.",
                },
                "stage": AAZStageEnum.Preview
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/databricks/workspace", json={
                "help": {
                    "short": "Commands to manage databricks workspace.",
                },
                "stage": AAZStageEnum.Preview
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/databricks/workspace/Leaves/create", json={
                "help": {
                    "short": "Create a new workspace.",
                },
                "stage": AAZStageEnum.Preview,
                "examples": [
                    {
                        "name": "Create a workspace",
                        "commands": [
                            "databricks workspace create --resource-group MyResourceGroup --name MyWorkspace --location westus --sku standard"
                        ]
                    },
                    {
                        "name": "Create a workspace with managed identity for storage account",
                        "commands": [
                            "databricks workspace create --resource-group MyResourceGroup --name MyWorkspace --location eastus2euap --sku premium --prepare-encryption"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/databricks/workspace/Leaves/update", json={
                "help": {
                    "short": "Update the workspace.",
                },
                "stage": AAZStageEnum.Preview,
                "examples": [
                    {
                        "name": "Update the workspace's tags.",
                        "commands": [
                            "databricks workspace update --resource-group MyResourceGroup --name MyWorkspace --tags {key1:value1,key2:value2}"
                        ]
                    },
                    {
                        "name": "Clean the workspace's tags.",
                        "commands": [
                            "databricks workspace update --resource-group MyResourceGroup --name MyWorkspace --tags {}"
                        ]
                    },
                    {
                        "name": "Prepare for CMK encryption by assigning identity for storage account.",
                        "commands": [
                            "databricks workspace update --resource-group MyResourceGroup --name MyWorkspace --prepare-encryption"
                        ]
                    },
                    {
                        "name": "Configure CMK encryption.",
                        "commands": [
                            "databricks workspace update --resource-group MyResourceGroup --name MyWorkspace --key-source Microsoft.KeyVault -key-name MyKey --key-vault https://myKeyVault.vault.azure.net/ --key-version 00000000000000000000000000000000"
                        ]
                    },
                    {
                        "name": "Revert encryption to Microsoft Managed Keys.",
                        "commands": [
                            "databricks workspace update --resource-group MyResourceGroup --name MyWorkspace --key-source Default"
                        ]
                    },
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/databricks/workspace/Leaves/delete", json={
                "help": {
                    "short": "Delete the workspace.",
                },
                "stage": AAZStageEnum.Preview,
                "examples": [
                    {
                        "name": "Delete the workspace.",
                        "commands": [
                            "databricks workspace delete --resource-group MyResourceGroup --name MyWorkspace"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/databricks/workspace/Leaves/show", json={
                "help": {
                    "short": "Show the workspace.",
                },
                "stage": AAZStageEnum.Preview,
                "examples": [
                    {
                        "name": "Show the workspace.",
                        "commands": [
                            "databricks workspace show --resource-group MyResourceGroup --name MyWorkspace"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/databricks/workspace/Leaves/list", json={
                "help": {
                    "short": "Get all the workspaces.",
                },
                "stage": AAZStageEnum.Preview,
                "examples": [
                    {
                        "name": "List workspaces within a resource group.",
                        "commands": [
                            "databricks workspace list --resource-group MyResourceGroup"
                        ]
                    },
                    {
                        "name": "List workspaces within the default subscription.",
                        "commands": [
                            "databricks workspace list"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/databricks/workspace/vnet-peering", json={
                "help": {
                    "short": "Commands to manage databricks workspace vnet peering.",
                },
                "stage": AAZStageEnum.Preview
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/databricks/workspace/vnet-peering/Leaves/create", json={
                "help": {
                    "short": "Create a vnet peering for a workspace.",
                },
                "stage": AAZStageEnum.Preview,
                "examples": [
                    {
                        "name": "Create a vnet peering for a workspace",
                        "commands": [
                            "databricks workspace vnet-peering create --resource-group MyResourceGroup --workspace-name MyWorkspace -n MyPeering --remote-vnet /subscriptions/000000-0000-0000/resourceGroups/MyRG/providers/Microsoft.Network/virtualNetworks/MyVNet"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/databricks/workspace/vnet-peering/Leaves/update", json={
                "help": {
                    "short": "Update the vnet peering.",
                },
                "stage": AAZStageEnum.Preview,
                "examples": [
                    {
                        "name": "Update the vnet peering (enable gateway transit and disable virtual network access).",
                        "commands": [
                            "databricks workspace vnet-peering update --resource-group MyResourceGroup --workspace-name MyWorkspace -n MyPeering --allow-gateway-transit --allow-virtual-network-access false",
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/databricks/workspace/vnet-peering/Leaves/list", json={
                "help": {
                    "short": "List vnet peerings under a workspace.",
                },
                "stage": AAZStageEnum.Preview,
                "examples": [
                    {
                        "name": "List vnet peerings under a workspace.",
                        "commands": [
                            "databricks workspace vnet-peering list --resource-group MyResourceGroup --workspace-name MyWorkspace",
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/databricks/workspace/vnet-peering/Leaves/delete", json={
                "help": {
                    "short": "Delete the vnet peering.",
                },
                "stage": AAZStageEnum.Preview,
                "examples": [
                    {
                        "name": "Delete the vnet peering.",
                        "commands": [
                            "databricks workspace vnet-peering delete --resource-group MyResourceGroup --workspace-name MyWorkspace -n MyPeering",
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/databricks/workspace/vnet-peering/Leaves/show", json={
                "help": {
                    "short": "Show the vnet peering.",
                },
                "stage": AAZStageEnum.Preview,
                "examples": [
                    {
                        "name": "Show the vnet peering.",
                        "commands": [
                            "databricks workspace vnet-peering show --resource-group MyResourceGroup --workspace-name MyWorkspace -n MyPeering",
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.post(f"{ws_url}/Generate")
            self.assertTrue(rv.status_code == 200)

    @workspace_name("test_workspace_aaz_generate_elastic")
    def test_workspace_aaz_generate_elastic(self, ws_name):
        with self.app.test_client() as c:
            rv = c.post(f"/AAZ/Editor/Workspaces", json={
                "name": ws_name,
                "plane": PlaneEnum.Mgmt,
            })
            self.assertTrue(rv.status_code == 200)
            ws = rv.get_json()
            ws_url = ws['url']
            rv = c.post(f"{ws_url}/CommandTree/Nodes/aaz/AddSwagger", json={
                'module': 'elastic',
                'version': '2020-07-01',
                'resources': [
                    {'id': swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/providers/Microsoft.Elastic/monitors')},
                    {'id': swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Elastic/monitors')},
                    {'id': swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Elastic/monitors/{monitorName}')},
                    {'id': swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Elastic/monitors/{monitorName}/listMonitoredResources')},
                    {'id': swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Elastic/monitors/{monitorName}/listDeploymentInfo')},
                    {'id': swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Elastic/monitors/{monitorName}/tagRules')},
                    {'id': swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Elastic/monitors/{monitorName}/tagRules/{ruleSetName}')},
                    {'id': swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Elastic/monitors/{monitorName}/listVMHost')},
                    {'id': swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Elastic/monitors/{monitorName}/vmIngestionDetails')},
                    {'id': swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Elastic/monitors/{monitorName}/vmCollectionUpdate')},
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.post(f"{ws_url}/CommandTree/Nodes/aaz/elastic/monitor/Leaves/list-monitored-resource/Rename", json={
                'name': "elastic monitor list-resource"
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.post(f"{ws_url}/CommandTree/Nodes/aaz/elastic/monitor/Leaves/vm-collection-update/Rename", json={
                'name': "elastic monitor update-vm-collection"
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.post(f"{ws_url}/CommandTree/Nodes/aaz/elastic/monitor/Leaves/vm-ingestion-detail/Rename", json={
                'name': "elastic monitor list-vm-ingestion-detail"
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.get(f"{ws_url}/CommandTree/Nodes/aaz")
            self.assertTrue(rv.status_code == 200)
            command_tree = rv.get_json()

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic", json={
                "help": {
                    "short": "Manage Microsoft Elastic.",
                },
                "stage": AAZStageEnum.Experimental
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic/monitor", json={
                "help": {
                    "short": "Manage monitor with Elastic.",
                },
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic/monitor/tag-rule", json={
                "help": {
                    "short": "Manage tag rule with Elastic.",
                },
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic/monitor/Leaves/list", json={
                "help": {
                    "short": "List all monitors under the specified resource group. "
                             "And List all monitors under the specified subscription.",
                },
                "examples": [
                    {
                        "name": "Monitors List By ResourceGroup",
                        "commands": [
                            "elastic monitor list --resource-group myResourceGroup"
                        ]
                    },
                    {
                        "name": "Monitors List",
                        "commands": [
                            "elastic monitor list"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic/monitor/Leaves/show", json={
                "help": {
                    "short": "Get the properties of a specific monitor resource.",
                },
                "examples": [
                    {
                        "name": "Monitors Get",
                        "commands": [
                            "elastic monitor show --name myMonitor --resource-group myResourceGroup"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic/monitor/Leaves/create", json={
                "help": {
                    "short": "Create a monitor resource.",
                },
                "examples": [
                    {
                        "name": "Monitors Create",
                        "commands": [
                            "elastic monitor create --name myMonitor --location westus2"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic/monitor/Leaves/update", json={
                "help": {
                    "short": "Update a monitor resource.",
                },
                "examples": [
                    {
                        "name": "Monitors Update",
                        "commands": [
                            "elastic monitor update --name myMonitor --tags Environment=dev --resource-group myResourceGroup"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic/monitor/Leaves/delete", json={
                "help": {
                    "short": "Delete a monitor resource.",
                },
                "examples": [
                    {
                        "name": "Monitors Delete",
                        "commands": [
                            "elastic monitor delete --name myMonitor --resource-group myResourceGroup"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic/monitor/Leaves/list-deployment-info", json={
                "help": {
                    "short": "Fetch information regarding Elastic cloud deployment corresponding to the Elastic monitor resource.",
                },
                "examples": [
                    {
                        "name": "DeploymentInfo List",
                        "commands": [
                            "elastic monitor list-deployment-info --name myMonitor --resource-group myResourceGroup"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic/monitor/Leaves/list-resource", json={
                "help": {
                    "short": "List the resources currently being monitored by the Elastic monitor resource.",
                },
                "examples": [
                    {
                        "name": "MonitoredResources List",
                        "commands": [
                            "elastic monitor list-resource --name myMonitor --resource-group myResourceGroup"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic/monitor/Leaves/list-vm-host", json={
                "help": {
                    "short": "List the vm resources currently being monitored by the Elastic monitor resource.",
                },
                "examples": [
                    {
                        "name": "VMHost List",
                        "commands": [
                            "elastic monitor list-vm-host --name myMonitor --resource-group myResourceGroup"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic/monitor/Leaves/list-vm-ingestion-detail", json={
                "help": {
                    "short": "List the vm ingestion details that will be monitored by the Elastic monitor resource.",
                },
                "examples": [
                    {
                        "name": "VMIngestion Details",
                        "commands": [
                            "elastic monitor list-vm-ingestion-detail --name myMonitor --resource-group myResourceGroup"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic/monitor/Leaves/update-vm-collection", json={
                "help": {
                    "short": "Update the vm details that will be monitored by the Elastic monitor resource.",
                },
                "examples": [
                    {
                        "name": "VMCollection Update",
                        "commands": [
                            "elastic monitor update-vm-collection --name myMonitor --resource-group myResourceGroup "
                            "--operation-name Add --vm-resource-id /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/myResourceGroup/providers/Microsoft.Compute/virtualmachines/myVM"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic/monitor/tag-rule/Leaves/list", json={
                "help": {
                    "short": "List the tag rules for a given monitor resource.",
                },
                "examples": [
                    {
                        "name": "TagRules List",
                        "commands": [
                            "elastic monitor tag-rule list --monitor-name myMonitor --resource-group myResourceGroup"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic/monitor/tag-rule/Leaves/show", json={
                "help": {
                    "short": "Get a tag rule set for a given monitor resource.",
                },
                "examples": [
                    {
                        "name": "TagRules Get",
                        "commands": [
                            "elastic monitor tag-rule show --monitor-name myMonitor --resource-group myResourceGroup --rule-set-name default"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic/monitor/tag-rule/Leaves/create", json={
                "help": {
                    "short": "Create a tag rule set for a given monitor resource.",
                },
                "examples": [
                    {
                        "name": "TagRules Create",
                        "commands": [
                            "elastic monitor tag-rule create --monitor-name myMonitor --resource-group myResourceGroup "
                            "--rule-set-name default --filtering-tags name=Environment action=Include value=Prod "
                            "--send-aad-logs False --send-activity-logs --send-subscription-logs "
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic/monitor/tag-rule/Leaves/update", json={
                "help": {
                    "short": "Update a tag rule set for a given monitor resource.",
                },
                "examples": [
                    {
                        "name": "TagRules Update",
                        "commands": [
                            "elastic monitor tag-rule update --monitor-name myMonitor --resource-group myResourceGroup "
                            "--rule-set-name default --send-aad-logs True"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic/monitor/tag-rule/Leaves/delete", json={
                "help": {
                    "short": "Delete a tag rule set for a given monitor resource.",
                },
                "examples": [
                    {
                        "name": "TagRules Delete",
                        "commands": [
                            "elastic monitor tag-rule delete --monitor-name myMonitor --resource-group myResourceGroup "
                            "--rule-set-name default"
                        ]
                    }
                ]
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
                    {'id': swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/providers/Microsoft.EdgeOrder/addresses')},
                    {'id': swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/providers/Microsoft.EdgeOrder/listProductFamilies')},
                    {'id': swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/providers/Microsoft.EdgeOrder/listConfigurations')},
                    {'id': swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/providers/Microsoft.EdgeOrder/productFamiliesMetadata')},
                    {'id': swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/providers/Microsoft.EdgeOrder/orders')},
                    {'id': swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/providers/Microsoft.EdgeOrder/orderItems')},
                    {'id': swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.EdgeOrder/addresses')},
                    {'id': swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.EdgeOrder/addresses/{addressName}')},
                    {'id': swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.EdgeOrder/orders')},
                    {'id': swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.EdgeOrder/locations/{location}/orders/{orderName}')},
                    {'id': swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.EdgeOrder/orderItems')},
                    {'id': swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.EdgeOrder/orderItems/{orderItemName}')},
                    {'id': swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.EdgeOrder/orderItems/{orderItemName}/cancel')},
                    {'id': swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.EdgeOrder/orderItems/{orderItemName}/return')},
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
                    {'id': swagger_resource_path_to_resource_id(
                        '/providers/Microsoft.EdgeOrder/operations')},
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
