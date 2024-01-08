import json
import os

from command.controller.workspace_cfg_editor import WorkspaceCfgEditor
from command.controller.workspace_manager import WorkspaceManager
from command.tests.common import CommandTestCase, workspace_name
from swagger.utils.tools import swagger_resource_path_to_resource_id
from swagger.utils.source import SourceTypeEnum
from utils.base64 import b64encode_str
from utils.plane import PlaneEnum
from utils.client import CloudEnum
from utils.stage import AAZStageEnum
from command.model.configuration import DEFAULT_CONFIRMATION_PROMPT


class APIEditorTest(CommandTestCase):

    @workspace_name("test_workspaces_1", arg_name="name1")
    @workspace_name("test_workspaces_2", arg_name="name2")
    def test_workspaces(self, name1, name2):
        with self.app.test_client() as c:
            rv = c.post(f"/AAZ/Editor/Workspaces", json={
                "name": name1,
                "plane": PlaneEnum.Mgmt,
                "modNames": "edgeorder",
                "resourceProvider": "Microsoft.EdgeOrder",
                "source": SourceTypeEnum.OpenAPI,
            })
            assert rv.status_code == 200
            ws1 = rv.get_json()
            assert ws1['name'] == name1
            assert ws1['plane'] == PlaneEnum.Mgmt
            assert ws1['modNames'] == "edgeorder"
            assert ws1['resourceProvider'] == "Microsoft.EdgeOrder"
            assert ws1['source'] == SourceTypeEnum.OpenAPI
            assert ws1['version']
            assert ws1['url']
            assert ws1['commandTree']['names'] == ['aaz']
            assert os.path.exists(ws1['folder'])

            rv = c.post(f"/AAZ/Editor/Workspaces", json={
                "name": name2,
                "plane": PlaneEnum.Mgmt,
                "modNames": "edgeorder",
                "resourceProvider": "Microsoft.EdgeOrder",
                "source": SourceTypeEnum.OpenAPI,
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
                "modNames": "edgeorder",
                "resourceProvider": "Microsoft.EdgeOrder",
                "source": SourceTypeEnum.OpenAPI,
            })
            assert rv.status_code == 409

    @workspace_name("test_workspace_1")
    def test_workspace(self, ws_name):
        with self.app.test_client() as c:
            rv = c.post(f"/AAZ/Editor/Workspaces", json={
                "name": ws_name,
                "plane": PlaneEnum.Mgmt,
                "modNames": "edgeorder",
                "resourceProvider": "Microsoft.EdgeOrder",
                "source": SourceTypeEnum.OpenAPI,
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
                "modNames": "edgeorder",
                "resourceProvider": "Microsoft.EdgeOrder",
                "source": SourceTypeEnum.OpenAPI,
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
            assert command['confirmation'] == DEFAULT_CONFIRMATION_PROMPT

            rv = c.get(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/address/Leaves/create")
            assert rv.status_code == 200
            command = rv.get_json()
            assert command['names'] == ['edge-order', 'address', 'create']
            assert len(command['argGroups']) == 3
            assert 'conditions' not in command
            assert len(command['operations']) == 1
            assert len(command['outputs']) == 1
            assert len(command['resources']) == 1
            assert command['version'] == '2021-12-01'

            rv = c.get(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/address/Leaves/update")
            assert rv.status_code == 200
            command = rv.get_json()
            assert command['names'] == ['edge-order', 'address', 'update']
            assert len(command['argGroups']) == 3
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
                "modNames": "edgeorder",
                "resourceProvider": "Microsoft.EdgeOrder",
                "source": SourceTypeEnum.OpenAPI,
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

            # try deleting one resource in list
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
                "modNames": "edgeorder",
                "resourceProvider": "Microsoft.EdgeOrder",
                "source": SourceTypeEnum.OpenAPI,
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
                "modNames": "edgeorder",
                "resourceProvider": "Microsoft.EdgeOrder",
                "source": SourceTypeEnum.OpenAPI,
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
                "modNames": "edgeorder",
                "resourceProvider": "Microsoft.EdgeOrder",
                "source": SourceTypeEnum.OpenAPI,
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
                "modNames": "databricks",
                "resourceProvider": "Microsoft.Databricks",
                "source": SourceTypeEnum.OpenAPI,
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
                "modNames": "elastic",
                "resourceProvider": "Microsoft.Elastic",
                "source": SourceTypeEnum.OpenAPI,
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
                "modNames": "edgeorder",
                "resourceProvider": "Microsoft.EdgeOrder",
                "source": SourceTypeEnum.OpenAPI,
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
                "modNames": "edgeorder",
                "resourceProvider": "Microsoft.EdgeOrder",
                "source": SourceTypeEnum.OpenAPI,
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
                    "short": "Manage edge order.",
                },
                "stage": AAZStageEnum.Preview
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/address/Leaves/list", json={
                "help": {
                    "short": "Manage edge order.",
                },
                "stage": AAZStageEnum.Preview
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.post(f"{ws_url}/Generate")
            self.assertTrue(rv.status_code == 200)

    @workspace_name("test_workspace_command_argument_modification")
    def test_workspace_command_argument_modification(self, ws_name):
        with self.app.test_client() as c:
            rv = c.post(f"/AAZ/Editor/Workspaces", json={
                "name": ws_name,
                "plane": PlaneEnum.Mgmt,
                "modNames": "databricks",
                "resourceProvider": "Microsoft.Databricks",
                "source": SourceTypeEnum.OpenAPI,
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

            rv = c.get(f"{ws_url}/CommandTree/Nodes/aaz/databricks/workspace/Leaves/create/Arguments/$Path.workspaceName")
            self.assertTrue(rv.status_code == 200)
            arg = rv.get_json()
            self.assertTrue(arg['var'] == '$Path.workspaceName')
            self.assertTrue(arg['options'] == ['n', 'name', 'workspace-name'])
            self.assertTrue(arg['idPart'] == 'name')
            self.assertTrue(arg['type'] == 'string')
            self.assertTrue(arg['required'] is True)
            rv = c.get(f"{ws_url}/CommandTree/Nodes/aaz/databricks/workspace/Leaves/create/Arguments/@WorkspaceCustomStringParameter_create.value")
            self.assertTrue(rv.status_code == 200)
            arg = rv.get_json()
            self.assertTrue(arg['options'] == ['value'])
            self.assertTrue(arg['required'] is True)
            self.assertTrue(arg['var'] == '@WorkspaceCustomStringParameter_create.value')
            self.assertTrue(arg['type'] == 'string')
            rv = c.get(f"{ws_url}/CommandTree/Nodes/aaz/databricks/workspace/Leaves/create/Arguments/$parameters.properties.parameters.encryption.value.keySource")
            self.assertTrue(rv.status_code == 200)
            arg = rv.get_json()
            self.assertTrue(arg['options'] == ['key-source'])
            self.assertTrue(arg['type'] == 'string')
            self.assertTrue(arg['var'] == '$parameters.properties.parameters.encryption.value.keySource')
            self.assertTrue(arg['default'] == {'value': 'Default'})
            self.assertTrue('enum' in arg)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/databricks/workspace/Leaves/create/Arguments/@WorkspaceCustomStringParameter_create.value", json={
                "options": ["v", "value"],
                "stage": AAZStageEnum.Experimental,
                "group": "Value",
                "help": {
                    "short": "value",
                    "lines": [
                        "The value which should be used.",
                        "Additional Line",
                    ]
                },
            })
            self.assertTrue(rv.status_code == 200)
            arg = rv.get_json()
            self.assertTrue(arg['options'] == ['v', 'value'])
            self.assertTrue(arg['stage'] == AAZStageEnum.Experimental)
            self.assertTrue(arg['help']['short'] == 'value')
            self.assertTrue(arg['help']['lines'] == ['The value which should be used.', 'Additional Line'])
            self.assertTrue(arg['group'] == 'Value')

            rv = c.patch(
                f"{ws_url}/CommandTree/Nodes/aaz/databricks/workspace/Leaves/create/Arguments/$Path.workspaceName",
                json={
                    "group": "ResourceName",
                })
            self.assertTrue(rv.status_code == 200)
            arg = rv.get_json()
            self.assertTrue(arg['group'] == 'ResourceName')

            rv = c.get(f"{ws_url}/CommandTree/Nodes/aaz/databricks/workspace/Leaves/create")
            self.assertTrue(rv.status_code == 200)
            command = rv.get_json()
            self.assertTrue("ResourceName" in {arg_group['name'] for arg_group in command['argGroups']})

            # add help to generate command
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

    @workspace_name("test_workspace_command_argument_find_similar")
    def test_workspace_command_argument_find_similar(self, ws_name):
        api_version = '2021-04-01-preview'
        module = 'databricks'
        with self.app.test_client() as c:
            rv = c.post(f"/AAZ/Editor/Workspaces", json={
                "name": ws_name,
                "plane": PlaneEnum.Mgmt,
                "modNames": "databricks",
                "resourceProvider": "Microsoft.Databricks",
                "source": SourceTypeEnum.OpenAPI,
            })
            self.assertTrue(rv.status_code == 200)
            ws = rv.get_json()
            ws_url = ws['url']
            rv = c.post(f"{ws_url}/CommandTree/Nodes/aaz/AddSwagger", json={
                'module': module,
                'version': api_version,
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

            rv = c.post(f"{ws_url}/CommandTree/Nodes/aaz/databricks/Rename", json={
                'name': "data-bricks"
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.post(f"{ws_url}/CommandTree/Nodes/aaz/data-bricks/workspace/virtual-network-peering/Rename", json={
                'name': "data-bricks workspace vnet-peering"
            })
            self.assertTrue(rv.status_code == 200)

            manager = WorkspaceManager(ws_name)
            manager.load()
            leaf = manager.find_command_tree_leaf('data-bricks', 'workspace', 'create')
            cfg_editor = manager.load_cfg_editor_by_command(leaf)

            arg = cfg_editor.find_arg(*leaf.names, idx='workspace-name')

            rv = c.post(f"{ws_url}/CommandTree/Nodes/aaz/data-bricks/workspace/Leaves/create/Arguments/{arg.var}/FindSimilar")
            self.assertTrue(rv.status_code == 200)
            results = rv.get_json()
            self.assertEqual(results, {'aaz': {'commandGroups': {'data-bricks': {'commandGroups': {
                'workspace': {'commands': {
                    'create': {'args': {'$Path.workspaceName': ['workspace-name']}, 'id': f'/AAZ/Editor/Workspaces/{ws_name}/CommandTree/Nodes/aaz/data-bricks/workspace/Leaves/create', 'names': ['data-bricks', 'workspace', 'create']},
                    'delete': {'args': {'$Path.workspaceName': ['workspace-name']}, 'id': f'/AAZ/Editor/Workspaces/{ws_name}/CommandTree/Nodes/aaz/data-bricks/workspace/Leaves/delete', 'names': ['data-bricks', 'workspace', 'delete']},
                    'show': {'args': {'$Path.workspaceName': ['workspace-name']}, 'id': f'/AAZ/Editor/Workspaces/{ws_name}/CommandTree/Nodes/aaz/data-bricks/workspace/Leaves/show', 'names': ['data-bricks', 'workspace', 'show']},
                    'update': {'args': {'$Path.workspaceName': ['workspace-name']}, 'id': f'/AAZ/Editor/Workspaces/{ws_name}/CommandTree/Nodes/aaz/data-bricks/workspace/Leaves/update', 'names': ['data-bricks', 'workspace', 'update']}
                }, 'id': f'/AAZ/Editor/Workspaces/{ws_name}/CommandTree/Nodes/aaz/data-bricks/workspace'}}, 'id': f'/AAZ/Editor/Workspaces/{ws_name}/CommandTree/Nodes/aaz/data-bricks'}}, 'id': f'/AAZ/Editor/Workspaces/{ws_name}/CommandTree/Nodes/aaz'}})

            arg = cfg_editor.find_arg(*leaf.names, idx='resource-group')
            rv = c.post(f"{ws_url}/CommandTree/Nodes/aaz/data-bricks/workspace/Leaves/create/Arguments/{arg.var}/FindSimilar")
            self.assertTrue(rv.status_code == 200)
            results = rv.get_json()
            self.maxDiff = 100000
            self.assertEqual(results, {'aaz': {'commandGroups': {'data-bricks': {'commandGroups': {'workspace': {
                'commandGroups': {'vnet-peering': {'commands': {
                    'create': {'args': {'$Path.resourceGroupName': ['resource-group']}, 'id': f'/AAZ/Editor/Workspaces/{ws_name}/CommandTree/Nodes/aaz/data-bricks/workspace/vnet-peering/Leaves/create', 'names': ['data-bricks', 'workspace', 'vnet-peering', 'create']},
                    'delete': {'args': {'$Path.resourceGroupName': ['resource-group']}, 'id': f'/AAZ/Editor/Workspaces/{ws_name}/CommandTree/Nodes/aaz/data-bricks/workspace/vnet-peering/Leaves/delete', 'names': ['data-bricks', 'workspace', 'vnet-peering', 'delete']},
                    'list': {'args': {'$Path.resourceGroupName': ['resource-group']}, 'id': f'/AAZ/Editor/Workspaces/{ws_name}/CommandTree/Nodes/aaz/data-bricks/workspace/vnet-peering/Leaves/list', 'names': ['data-bricks', 'workspace', 'vnet-peering', 'list']},
                    'show': {'args': {'$Path.resourceGroupName': ['resource-group']}, 'id': f'/AAZ/Editor/Workspaces/{ws_name}/CommandTree/Nodes/aaz/data-bricks/workspace/vnet-peering/Leaves/show', 'names': ['data-bricks', 'workspace', 'vnet-peering', 'show']},
                    'update': {'args': {'$Path.resourceGroupName': ['resource-group']}, 'id': f'/AAZ/Editor/Workspaces/{ws_name}/CommandTree/Nodes/aaz/data-bricks/workspace/vnet-peering/Leaves/update', 'names': ['data-bricks', 'workspace', 'vnet-peering', 'update']}}, 'id': f'/AAZ/Editor/Workspaces/{ws_name}/CommandTree/Nodes/aaz/data-bricks/workspace/vnet-peering'}},
                'commands': {
                    'create': {'args': {'$Path.resourceGroupName': ['resource-group']}, 'id': f'/AAZ/Editor/Workspaces/{ws_name}/CommandTree/Nodes/aaz/data-bricks/workspace/Leaves/create', 'names': ['data-bricks', 'workspace', 'create']},
                    'delete': {'args': {'$Path.resourceGroupName': ['resource-group']}, 'id': f'/AAZ/Editor/Workspaces/{ws_name}/CommandTree/Nodes/aaz/data-bricks/workspace/Leaves/delete', 'names': ['data-bricks', 'workspace', 'delete']},
                    'list': {'args': {'$Path.resourceGroupName': ['resource-group']}, 'id': f'/AAZ/Editor/Workspaces/{ws_name}/CommandTree/Nodes/aaz/data-bricks/workspace/Leaves/list', 'names': ['data-bricks', 'workspace', 'list']},
                    'show': {'args': {'$Path.resourceGroupName': ['resource-group']}, 'id': f'/AAZ/Editor/Workspaces/{ws_name}/CommandTree/Nodes/aaz/data-bricks/workspace/Leaves/show', 'names': ['data-bricks', 'workspace', 'show']},
                    'update': {'args': {'$Path.resourceGroupName': ['resource-group']}, 'id': f'/AAZ/Editor/Workspaces/{ws_name}/CommandTree/Nodes/aaz/data-bricks/workspace/Leaves/update', 'names': ['data-bricks', 'workspace', 'update']}
                }, 'id': f'/AAZ/Editor/Workspaces/{ws_name}/CommandTree/Nodes/aaz/data-bricks/workspace'}}, 'id': f'/AAZ/Editor/Workspaces/{ws_name}/CommandTree/Nodes/aaz/data-bricks'}}, 'id': f'/AAZ/Editor/Workspaces/{ws_name}/CommandTree/Nodes/aaz'}})

            arg = cfg_editor.find_arg(*leaf.names, idx='authorizations[].principal-id')
            rv = c.post(
                f"{ws_url}/CommandTree/Nodes/aaz/data-bricks/workspace/Leaves/create/Arguments/{arg.var}/FindSimilar")
            self.assertTrue(rv.status_code == 200)
            results = rv.get_json()
            self.assertTrue(results, {'aaz': {'commandGroups': {'data-bricks': {'commandGroups': {'workspace': {'commands': {
                'create': {'args': {'$parameters.properties.authorizations[].principalId': ['authorizations[].principal-id']}, 'id': f'/AAZ/Editor/Workspaces/{ws_name}/CommandTree/Nodes/aaz/data-bricks/workspace/Leaves/create', 'names': ['data-bricks', 'workspace', 'create']},
                'update': {'args': {'$parameters.properties.authorizations[].principalId': ['authorizations[].principal-id']}, 'id': f'/AAZ/Editor/Workspaces/{ws_name}/CommandTree/Nodes/aaz/data-bricks/workspace/Leaves/update', 'names': ['data-bricks', 'workspace', 'update']}
            }, 'id': f'/AAZ/Editor/Workspaces/{ws_name}/CommandTree/Nodes/aaz/data-bricks/workspace'}}, 'id': f'/AAZ/Editor/Workspaces/{ws_name}/CommandTree/Nodes/aaz/data-bricks'}}, 'id': f'/AAZ/Editor/Workspaces/{ws_name}/CommandTree/Nodes/aaz'}})

            arg = cfg_editor.find_arg(*leaf.names, idx='parameters.aml-workspace-id')
            rv = c.post(
                f"{ws_url}/CommandTree/Nodes/aaz/data-bricks/workspace/Leaves/create/Arguments/{arg.var}/FindSimilar")
            self.assertTrue(rv.status_code == 200)
            results = rv.get_json()
            self.assertEqual(results, {'aaz': {'commandGroups': {'data-bricks': {'commandGroups': {'workspace': {'commands': {
                'create': {'args': {'$parameters.properties.parameters.amlWorkspaceId': ['parameters.aml-workspace-id']}, 'id': f'/AAZ/Editor/Workspaces/{ws_name}/CommandTree/Nodes/aaz/data-bricks/workspace/Leaves/create', 'names': ['data-bricks', 'workspace', 'create']},
                'update': {'args': {'$parameters.properties.parameters.amlWorkspaceId': ['parameters.aml-workspace-id']}, 'id': f'/AAZ/Editor/Workspaces/{ws_name}/CommandTree/Nodes/aaz/data-bricks/workspace/Leaves/update', 'names': ['data-bricks', 'workspace', 'update']}
            }, 'id': f'/AAZ/Editor/Workspaces/{ws_name}/CommandTree/Nodes/aaz/data-bricks/workspace'}}, 'id': f'/AAZ/Editor/Workspaces/{ws_name}/CommandTree/Nodes/aaz/data-bricks'}}, 'id': f'/AAZ/Editor/Workspaces/{ws_name}/CommandTree/Nodes/aaz'}})

            arg = cfg_editor.find_arg(*leaf.names, idx='parameters.aml-workspace-id.value')
            rv = c.post(
                f"{ws_url}/CommandTree/Nodes/aaz/data-bricks/workspace/Leaves/create/Arguments/{arg.var}/FindSimilar")
            self.assertTrue(rv.status_code == 200)
            results = rv.get_json()
            self.assertEqual(results, {'aaz': {'commandGroups': {'data-bricks': {'commandGroups': {'workspace': {'commands': {
                'create': {'args': {'@WorkspaceCustomStringParameter_create.value': ['parameters.aml-workspace-id.value', 'parameters.custom-private-subnet-name.value', 'parameters.custom-public-subnet-name.value', 'parameters.custom-virtual-network-id.value', 'parameters.load-balancer-backend-pool-name.value', 'parameters.load-balancer-id.value', 'parameters.nat-gateway-name.value', 'parameters.public-ip-name.value', 'parameters.storage-account-name.value', 'parameters.storage-account-sku-name.value', 'parameters.vnet-address-prefix.value']}, 'id': f'/AAZ/Editor/Workspaces/{ws_name}/CommandTree/Nodes/aaz/data-bricks/workspace/Leaves/create', 'names': ['data-bricks', 'workspace', 'create']},
                'update': {'args': {'@WorkspaceCustomStringParameter_update.value': ['parameters.aml-workspace-id.value', 'parameters.custom-private-subnet-name.value', 'parameters.custom-public-subnet-name.value', 'parameters.custom-virtual-network-id.value', 'parameters.load-balancer-backend-pool-name.value', 'parameters.load-balancer-id.value', 'parameters.nat-gateway-name.value', 'parameters.public-ip-name.value', 'parameters.storage-account-name.value', 'parameters.storage-account-sku-name.value', 'parameters.vnet-address-prefix.value']}, 'id': f'/AAZ/Editor/Workspaces/{ws_name}/CommandTree/Nodes/aaz/data-bricks/workspace/Leaves/update', 'names': ['data-bricks', 'workspace', 'update']}
            }, 'id': f'/AAZ/Editor/Workspaces/{ws_name}/CommandTree/Nodes/aaz/data-bricks/workspace'}}, 'id': f'/AAZ/Editor/Workspaces/{ws_name}/CommandTree/Nodes/aaz/data-bricks'}}, 'id': f'/AAZ/Editor/Workspaces/{ws_name}/CommandTree/Nodes/aaz'}})

            leaf = manager.find_command_tree_leaf('data-bricks', 'workspace', 'vnet-peering', 'create')
            cfg_editor = manager.load_cfg_editor_by_command(leaf)

            arg = cfg_editor.find_arg(*leaf.names, idx='databricks-address-space')
            rv = c.post(
                f"{ws_url}/CommandTree/Nodes/aaz/data-bricks/workspace/vnet-peering/Leaves/create/Arguments/{arg.var}/FindSimilar")
            self.assertTrue(rv.status_code == 200)
            results = rv.get_json()
            self.assertEqual(results, {'aaz': {'commandGroups': {'data-bricks': {'commandGroups': {'workspace': {'commandGroups': {'vnet-peering': {'commands': {
                'create': {'args': {'$VirtualNetworkPeeringParameters.properties.databricksAddressSpace': ['databricks-address-space']}, 'id': f'/AAZ/Editor/Workspaces/{ws_name}/CommandTree/Nodes/aaz/data-bricks/workspace/vnet-peering/Leaves/create', 'names': ['data-bricks', 'workspace', 'vnet-peering', 'create']},
                'update': {'args': {'$VirtualNetworkPeeringParameters.properties.databricksAddressSpace': ['databricks-address-space']}, 'id': f'/AAZ/Editor/Workspaces/{ws_name}/CommandTree/Nodes/aaz/data-bricks/workspace/vnet-peering/Leaves/update', 'names': ['data-bricks', 'workspace', 'vnet-peering', 'update']}
            }, 'id': f'/AAZ/Editor/Workspaces/{ws_name}/CommandTree/Nodes/aaz/data-bricks/workspace/vnet-peering'}}, 'id': f'/AAZ/Editor/Workspaces/{ws_name}/CommandTree/Nodes/aaz/data-bricks/workspace'}}, 'id': f'/AAZ/Editor/Workspaces/{ws_name}/CommandTree/Nodes/aaz/data-bricks'}}, 'id': f'/AAZ/Editor/Workspaces/{ws_name}/CommandTree/Nodes/aaz'}})

            arg = cfg_editor.find_arg(*leaf.names, idx='databricks-address-space.address-prefixes')
            rv = c.post(
                f"{ws_url}/CommandTree/Nodes/aaz/data-bricks/workspace/vnet-peering/Leaves/create/Arguments/{arg.var}/FindSimilar")
            self.assertTrue(rv.status_code == 200)
            results = rv.get_json()
            self.assertEqual(results, {'aaz': {'commandGroups': {'data-bricks': {'commandGroups': {'workspace': {'commandGroups': {'vnet-peering': {'commands': {
                'create': {'args': {'@AddressSpace_create.addressPrefixes': ['databricks-address-space.address-prefixes', 'remote-address-space.address-prefixes']}, 'id': f'/AAZ/Editor/Workspaces/{ws_name}/CommandTree/Nodes/aaz/data-bricks/workspace/vnet-peering/Leaves/create', 'names': ['data-bricks', 'workspace', 'vnet-peering', 'create']},
                'update': {'args': {'@AddressSpace_update.addressPrefixes': ['databricks-address-space.address-prefixes', 'remote-address-space.address-prefixes']}, 'id': f'/AAZ/Editor/Workspaces/{ws_name}/CommandTree/Nodes/aaz/data-bricks/workspace/vnet-peering/Leaves/update', 'names': ['data-bricks', 'workspace', 'vnet-peering', 'update']}
            }, 'id': f'/AAZ/Editor/Workspaces/{ws_name}/CommandTree/Nodes/aaz/data-bricks/workspace/vnet-peering'}}, 'id': f'/AAZ/Editor/Workspaces/{ws_name}/CommandTree/Nodes/aaz/data-bricks/workspace'}}, 'id': f'/AAZ/Editor/Workspaces/{ws_name}/CommandTree/Nodes/aaz/data-bricks'}}, 'id': f'/AAZ/Editor/Workspaces/{ws_name}/CommandTree/Nodes/aaz'}})

    @workspace_name("test_workspace_add_subresource_commands")
    def test_workspace_add_subresource_commands(self, ws_name):
        module = "cdn"
        api_version = '2021-06-01'
        with self.app.test_client() as c:
            rv = c.post(f"/AAZ/Editor/Workspaces", json={
                "name": ws_name,
                "plane": PlaneEnum.Mgmt,
                "modNames": module,
                "resourceProvider": "Microsoft.Cdn",
                "source": SourceTypeEnum.OpenAPI,
            })
            self.assertTrue(rv.status_code == 200)
            ws = rv.get_json()
            ws_url = ws['url']
            resource_id = swagger_resource_path_to_resource_id('/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Cdn/profiles/{profileName}/endpoints/{endpointName}')
            rv = c.post(f"{ws_url}/CommandTree/Nodes/aaz/AddSwagger", json={
                'module': module,
                'version': api_version,
                'resources': [
                    {'id': resource_id},
                    {'id': swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Cdn/profiles/{profileName}/endpoints')},
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.post(f"{ws_url}/Resources/{b64encode_str(resource_id)}/V/{b64encode_str(api_version)}/Subresources", json={
                'arg': '$endpoint.properties.originGroups',
                'commandGroupName': 'cdn profile endpoint origin-group',
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.get(f"{ws_url}/CommandTree/Nodes/aaz")
            self.assertTrue(rv.status_code == 200)
            node = rv.get_json()
            cg = node['commandGroups']
            self.assertTrue(len(cg) == 1 and 'cdn' in cg)

            cg = cg['cdn']['commandGroups']['profile']['commandGroups']['endpoint']['commandGroups']
            self.assertTrue(len(cg) == 1 and 'origin-group' in cg)
            commands = cg['origin-group']['commands']
            self.assertTrue(len(commands) == 5 and set(commands.keys()) == {'create', 'delete', 'list', 'show', 'update'})
            for cmd_name in ('create', 'delete', 'show', 'update'):
                self.assertEqual(len(commands[cmd_name]['resources']), 1)
                self.assertEqual(commands[cmd_name]['resources'][0]['version'], api_version)
                self.assertEqual(commands[cmd_name]['resources'][0]['id'], resource_id)
                self.assertEqual(commands[cmd_name]['resources'][0]['subresource'], 'properties.originGroups[]')
            for cmd_name in ('list',):
                self.assertEqual(len(commands[cmd_name]['resources']), 1)
                self.assertEqual(commands[cmd_name]['resources'][0]['version'], api_version)
                self.assertEqual(commands[cmd_name]['resources'][0]['id'], resource_id)
                self.assertEqual(commands[cmd_name]['resources'][0]['subresource'], 'properties.originGroups')

            rv = c.get(f"{ws_url}/Resources/{b64encode_str(resource_id)}/V/{b64encode_str(api_version)}/Commands")
            self.assertTrue(rv.status_code == 200)
            data = rv.get_json()
            self.assertTrue(len(data) == 9)

            rv = c.get(f"{ws_url}/Resources/{b64encode_str(resource_id)}/V/{b64encode_str(api_version)}/Subresources/{b64encode_str('properties.originGroups')}/Commands")
            self.assertTrue(rv.status_code == 200)
            data = rv.get_json()
            self.assertTrue(len(data) == 1)

            rv = c.get(
                f"{ws_url}/Resources/{b64encode_str(resource_id)}/V/{b64encode_str(api_version)}/Subresources/{b64encode_str('properties.originGroups[]')}/Commands")
            self.assertTrue(rv.status_code == 200)
            data = rv.get_json()
            self.assertTrue(len(data) == 4)

            rv = c.delete(
                f"{ws_url}/Resources/{b64encode_str(resource_id)}/V/{b64encode_str(api_version)}/Subresources/{b64encode_str('properties.originGroups')}")
            self.assertTrue(rv.status_code == 200)

            rv = c.get(f"{ws_url}/Resources/{b64encode_str(resource_id)}/V/{b64encode_str(api_version)}/Commands")
            self.assertTrue(rv.status_code == 200)
            data = rv.get_json()
            self.assertTrue(len(data) == 8)

            rv = c.delete(
                f"{ws_url}/Resources/{b64encode_str(resource_id)}/V/{b64encode_str(api_version)}/Subresources/{b64encode_str('properties.originGroups[]')}")
            self.assertTrue(rv.status_code == 200)

            rv = c.get(f"{ws_url}/Resources/{b64encode_str(resource_id)}/V/{b64encode_str(api_version)}/Commands")
            self.assertTrue(rv.status_code == 200)
            data = rv.get_json()
            self.assertTrue(len(data) == 4)

    @workspace_name("test_dataplane_workspace")
    def test_dataplane_workspace(self, ws_name):
        module = "codesigning"
        resource_provider = "Azure.CodeSigning"
        api_version = '2023-06-15-preview'
        with self.app.test_client() as c:
            rv = c.post(f"/AAZ/Editor/Workspaces", json={
                "name": ws_name,
                "plane": PlaneEnum._Data,
                "modNames": module,
                "resourceProvider": resource_provider,
                "source": SourceTypeEnum.OpenAPI,
            })
            self.assertTrue(rv.status_code == 200)
            ws = rv.get_json()
            self.assertEqual(ws['plane'], PlaneEnum.Data(resource_provider))
            self.assertEqual(ws['resourceProvider'], resource_provider)
            self.assertEqual(ws['modNames'], module)
            ws_url = ws['url']

            # add client configuration
            rv = c.get(f"{ws_url}/ClientConfig")
            self.assertTrue(rv.status_code == 404)

            rv = c.post(f"{ws_url}/ClientConfig", json={
                "auth": {
                    "aad": {
                        "scopes": ["https://codesigning.azure.net/.default"]
                    }
                },
                "templates": [
                    {
                        "cloud": CloudEnum.AzureCloud,
                        "template": "https://{region}.codesigning.azure.net/"
                    },
                    {
                        "cloud": CloudEnum.AzureChinaCloud,
                        "template": "https://{region}.codesigning.chinacloudapi.cn"
                    },
                    {
                        "cloud": CloudEnum.AzureUSGovernment,
                        "template": "https://{region}.codesigning.usgovcloudapi.us"
                    },
                    {
                        "cloud": CloudEnum.AzureGermanCloud,
                        "template": "https://{region}.codesigning.cloudapi.de"
                    },
                ],
            })
            self.assertTrue(rv.status_code == 200)

            client_config = rv.get_json()
            self.assertEqual(client_config['endpoints']['templates'], [
                {'cloud': 'AzureChinaCloud', 'template': 'https://{region}.codesigning.chinacloudapi.cn'},
                {'cloud': 'AzureCloud', 'template': 'https://{region}.codesigning.azure.net'},
                {'cloud': 'AzureGermanCloud', 'template': 'https://{region}.codesigning.cloudapi.de'},
                {'cloud': 'AzureUSGovernment', 'template': 'https://{region}.codesigning.usgovcloudapi.us'}
            ])
            self.assertEqual(client_config['endpoints']['params'], [
                {'arg': '$Client.Endpoint.region', 'name': 'region', 'required': True, 'skipUrlEncoding': True, 'type': 'string'}
            ])
            self.assertEqual(client_config['argGroup']['args'], [
                {'group': 'Client', 'options': ['region'], 'required': True, 'type': 'string', 'var': '$Client.Endpoint.region'}
            ])

            # update client arguments
            rv = c.get(f"{ws_url}/ClientConfig/Arguments/$Client.Endpoint.region")
            self.assertTrue(rv.status_code == 200)
            client_arg = rv.get_json()
            self.assertEqual(client_arg, {'group': 'Client', 'options': ['region'], 'required': True, 'type': 'string', 'var': '$Client.Endpoint.region'})
            rv = c.patch(f"{ws_url}/ClientConfig/Arguments/$Client.Endpoint.region", json={
                "options": ["region", "r"],
                "default": {
                    "value": "global"
                },
                "help": {
                    "short": "The Azure region wherein requests for signing will be sent."
                }
            })
            self.assertTrue(rv.status_code == 200)
            client_arg = rv.get_json()
            self.assertEqual(client_arg, {
                'default': {'value': 'global'},
                'help': {'short': 'The Azure region wherein requests for signing will be sent.'},
                'options': ['r', 'region'],
                'group': 'Client',
                'required': True,
                'type': 'string',
                'var': '$Client.Endpoint.region'
            })

            # add resources
            rv = c.post(f"{ws_url}/CommandTree/Nodes/aaz/AddSwagger", json={
                'module': module,
                'version': api_version,
                'resources': [
                    {'id': swagger_resource_path_to_resource_id('/codesigningaccounts/{codeSigningAccountName}/certificateprofiles/{certificateProfileName}:sign')},
                    {'id': swagger_resource_path_to_resource_id('/codesigningaccounts/{codeSigningAccountName}/certificateprofiles/{certificateProfileName}/sign/eku')},
                    {'id': swagger_resource_path_to_resource_id('/codesigningaccounts/{codeSigningAccountName}/certificateprofiles/{certificateProfileName}/sign/{operationId}')},
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.get(f"{ws_url}/CommandTree/Nodes/aaz")
            self.assertTrue(rv.status_code == 200)
            command_tree = rv.get_json()

            # modify command tree
            rv = c.post(
                f"{ws_url}/CommandTree/Nodes/aaz/code-signing/codesigningaccount/certificateprofile/sign-untitled1/eku/Leaves/list/Rename",
                json={
                    "name": "code-signing account certificate-profile list-eku"
                })
            self.assertTrue(rv.status_code == 200)

            rv = c.post(
                f"{ws_url}/CommandTree/Nodes/aaz/code-signing/codesigningaccount/certificateprofile/sign-untitled2/Leaves/show/Rename",
                json={
                    "name": "code-signing account certificate-profile sign-result"
                })
            self.assertTrue(rv.status_code == 200)
            rv = c.post(
                f"{ws_url}/CommandTree/Nodes/aaz/code-signing/codesigningaccount/certificateprofile/Leaves/sign/Rename",
                json={
                    "name": "code-signing account certificate-profile sign"
                })
            self.assertTrue(rv.status_code == 200)

            rv = c.delete(f"{ws_url}/CommandTree/Nodes/aaz/code-signing/codesigningaccount")
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/code-signing", json={
                "help": {
                    "short": "test"
                }
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/code-signing/account", json={
                "help": {
                    "short": "test"
                }
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/code-signing/account/certificate-profile", json={
                "help": {
                    "short": "test"
                }
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.get(f"{ws_url}/CommandTree/Nodes/aaz")
            self.assertTrue(rv.status_code == 200)
            command_tree = rv.get_json()

            rv = c.post(f"{ws_url}/Generate")
            self.assertTrue(rv.status_code == 200)

            # create a new workspace which should inherit client config
            rv = c.post(f"/AAZ/Editor/Workspaces", json={
                "name": ws_name + "_another",
                "plane": PlaneEnum._Data,
                "modNames": module,
                "resourceProvider": resource_provider,
                "source": SourceTypeEnum.OpenAPI,
            })
            self.assertTrue(rv.status_code == 200)
            ws2 = rv.get_json()
            self.assertEqual(ws2['plane'], PlaneEnum.Data(resource_provider))
            self.assertEqual(ws2['resourceProvider'], resource_provider)
            self.assertEqual(ws2['modNames'], module)
            ws_url2 = ws2['url']

            rv = c.get(f"{ws_url2}/ClientConfig")
            self.assertTrue(rv.status_code == 200)
            client_config = rv.get_json()
            self.assertEqual(client_config['endpoints']['templates'], [
                {'cloud': 'AzureChinaCloud', 'template': 'https://{region}.codesigning.chinacloudapi.cn'},
                {'cloud': 'AzureCloud', 'template': 'https://{region}.codesigning.azure.net'},
                {'cloud': 'AzureGermanCloud', 'template': 'https://{region}.codesigning.cloudapi.de'},
                {'cloud': 'AzureUSGovernment', 'template': 'https://{region}.codesigning.usgovcloudapi.us'}
            ])
            self.assertEqual(client_config['endpoints']['params'], [
                {'arg': '$Client.Endpoint.region', 'name': 'region', 'required': True, 'skipUrlEncoding': True, 'type': 'string'}
            ])
            self.assertEqual(client_config['argGroup']['args'], [
                {
                    'default': {'value': 'global'},
                    'help': {'short': 'The Azure region wherein requests for signing will be sent.'},
                    'options': ['r', 'region'],
                    'required': True,
                    'group': 'Client',
                    'type': 'string',
                    'var': '$Client.Endpoint.region'
                }
            ])

            rv = c.post(f"{ws_url2}/Generate")
            self.assertTrue(rv.status_code == 200)

            # test reload
            # update in ws 1
            rv = c.patch(f"{ws_url}/ClientConfig/Arguments/$Client.Endpoint.region", json={
                "options": ["region"]})
            self.assertTrue(rv.status_code == 200)
            client_arg = rv.get_json()
            self.assertEqual(client_arg, {
                'default': {'value': 'global'},
                'help': {'short': 'The Azure region wherein requests for signing will be sent.'},
                'options': ['region'],
                'group': 'Client',
                'required': True,
                'type': 'string',
                'var': '$Client.Endpoint.region'
            })

            rv = c.post(f"{ws_url}/Generate")
            self.assertTrue(rv.status_code == 200)

            # outdated version is not allowed
            rv = c.post(f"{ws_url2}/Generate")
            self.assertTrue(rv.status_code == 400)

            rv = c.post(f"{ws_url2}/ClientConfig/AAZ/Compare")
            self.assertTrue(rv.status_code == 409)

            # refresh in ws 2
            rv = c.post(f"{ws_url2}/ClientConfig/AAZ/Inherit")
            self.assertTrue(rv.status_code == 200)
            client_config = rv.get_json()
            self.assertEqual(client_config['argGroup']['args'], [
                {
                    'default': {'value': 'global'},
                    'help': {'short': 'The Azure region wherein requests for signing will be sent.'},
                    'options': ['region'],
                    'group': 'Client',
                    'required': True,
                    'type': 'string',
                    'var': '$Client.Endpoint.region'
                }
            ])

            rv = c.post(f"{ws_url2}/Generate")
            self.assertTrue(rv.status_code == 200)

    @workspace_name("test_dataplane_monitor_metrics")
    def test_dataplane_monitor_metrics(self, ws_name):
        module = "monitor"
        resource_provider = "Microsoft.Insights"
        api_version = '2023-05-01-preview'
        with self.app.test_client() as c:
            rv = c.post(f"/AAZ/Editor/Workspaces", json={
                "name": ws_name,
                "plane": PlaneEnum._Data,
                "modNames": module,
                "resourceProvider": resource_provider,
                "source": SourceTypeEnum.OpenAPI,
            })
            self.assertTrue(rv.status_code == 200)
            ws = rv.get_json()
            self.assertEqual(ws['plane'], PlaneEnum.Data(resource_provider))
            self.assertEqual(ws['resourceProvider'], resource_provider)
            self.assertEqual(ws['modNames'], module)
            ws_url = ws['url']

            # add client configuration
            rv = c.post(f"{ws_url}/ClientConfig", json={
                "auth": {
                    "aad": {
                        "scopes": ["https://metrics.monitor.azure.com/.default"]
                    }
                },
                "templates": [
                    {
                        "cloud": CloudEnum.AzureCloud,
                        "template": "https://{region}.metrics.monitor.azure.com/"
                    },
                    {
                        "cloud": CloudEnum.AzureChinaCloud,
                        "template": "https://{region}.metrics.monitor.chinacloudapi.cn"
                    },
                    {
                        "cloud": CloudEnum.AzureUSGovernment,
                        "template": "https://{region}.metrics.monitor.usgovcloudapi.us"
                    },
                    {
                        "cloud": CloudEnum.AzureGermanCloud,
                        "template": "https://{region}.metrics.monitor.cloudapi.de"
                    },
                ],
                "cloudMetadata": {
                    "selectorIndex": "suffixes.monitorMetrics",
                    "prefixTemplate": "https://{region}",
                }
            })
            self.assertTrue(rv.status_code == 200)

            client_config = rv.get_json()
            self.assertEqual(client_config['endpoints']['cloudMetadata'], {
                "selectorIndex": "suffixes.monitorMetrics",
                "prefixTemplate": "https://{region}",
            })

            # update client arguments
            rv = c.get(f"{ws_url}/ClientConfig/Arguments/$Client.Endpoint.region")
            self.assertTrue(rv.status_code == 200)
            client_arg = rv.get_json()
            self.assertEqual(client_arg, {'group': 'Client', 'options': ['region'], 'required': True, 'type': 'string',
                                          'var': '$Client.Endpoint.region'})

            # add resources
            rv = c.post(f"{ws_url}/CommandTree/Nodes/aaz/AddSwagger", json={
                'module': module,
                'version': api_version,
                'resources': [
                    {'id': swagger_resource_path_to_resource_id(
                        '/subscriptions/{}/metrics:getbatch')},
                ]
            })

            self.assertTrue(rv.status_code == 200)

            rv = c.get(f"{ws_url}/CommandTree/Nodes/aaz")
            self.assertTrue(rv.status_code == 200)
            command_tree = rv.get_json()

            # modify command tree
            rv = c.post(f"{ws_url}/CommandTree/Nodes/aaz/insights/Leaves/metricsget-batch/Rename", json={
                "name": "monitor metrics get-batch"
            })
            self.assertTrue(rv.status_code == 200)
            rv = c.delete(f"{ws_url}/CommandTree/Nodes/aaz/insights")
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/monitor", json={
                "help": {
                    "short": "test"
                }
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/monitor/metrics", json={
                "help": {
                    "short": "test"
                }
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.get(f"{ws_url}/CommandTree/Nodes/aaz")
            self.assertTrue(rv.status_code == 200)
            command_tree = rv.get_json()

            rv = c.post(f"{ws_url}/Generate")
            self.assertTrue(rv.status_code == 200)

    @workspace_name("test_mgmt_attestation")
    def test_mgmt_attestation(self, ws_name):
        module = "attestation"
        resource_provider = "Microsoft.Attestation"
        api_version = '2021-06-01-preview'

        with self.app.test_client() as c:
            rv = c.post(f"/AAZ/Editor/Workspaces", json={
                "name": ws_name,
                "plane": PlaneEnum.Mgmt,
                "modNames": module,
                "resourceProvider": resource_provider,
                "source": SourceTypeEnum.OpenAPI,
            })
            self.assertTrue(rv.status_code == 200)
            ws = rv.get_json()
            self.assertEqual(ws['plane'], PlaneEnum.Mgmt)
            self.assertEqual(ws['resourceProvider'], resource_provider)
            self.assertEqual(ws['modNames'], module)
            ws_url = ws['url']

            # add resources
            rv = c.post(f"{ws_url}/CommandTree/Nodes/aaz/AddSwagger", json={
                'module': module,
                'version': api_version,
                'resources': [
                    {'id': swagger_resource_path_to_resource_id('/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Attestation/attestationProviders/{providerName}')},
                    {'id': swagger_resource_path_to_resource_id('/subscriptions/{subscriptionId}/providers/Microsoft.Attestation/attestationProviders')},
                    {'id': swagger_resource_path_to_resource_id('/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Attestation/attestationProviders')},
                ]
            })
            self.assertTrue(rv.status_code == 200)

            command_tree = rv.get_json()

            # modify command tree
            rv = c.post(f"{ws_url}/CommandTree/Nodes/aaz/attestation/attestation-provider/Rename", json={
                "name": "attestation provider"
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/attestation", json={
                "help": {
                    "short": "test"
                }
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/attestation/provider", json={
                "help": {
                    "short": "test"
                }
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.get(f"{ws_url}/CommandTree/Nodes/aaz")
            self.assertTrue(rv.status_code == 200)
            command_tree = rv.get_json()

            rv = c.post(f"{ws_url}/Generate")
            self.assertTrue(rv.status_code == 200)

    @workspace_name("test_dataplane_attestation")
    def test_dataplane_attestation(self, ws_name):
        module = "attestation"
        resource_provider = "Microsoft.Attestation"
        api_version = '2022-09-01-preview'

        with self.app.test_client() as c:
            rv = c.post(f"/AAZ/Editor/Workspaces", json={
                "name": ws_name,
                "plane": PlaneEnum._Data,
                "modNames": module,
                "resourceProvider": resource_provider,
                "source": SourceTypeEnum.OpenAPI,
            })
            self.assertTrue(rv.status_code == 200)
            ws = rv.get_json()
            self.assertEqual(ws['plane'], PlaneEnum.Data(resource_provider))
            self.assertEqual(ws['resourceProvider'], resource_provider)
            self.assertEqual(ws['modNames'], module)
            ws_url = ws['url']

            # add client configuration
            rv = c.post(f"{ws_url}/ClientConfig", json={
                "auth": {
                    "aad": {
                        "scopes": ["https://attest.azure.net/.default"]
                    }
                },
                "resource": {
                    "plane": PlaneEnum.Mgmt,
                    "module": module,
                    "id": swagger_resource_path_to_resource_id('/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Attestation/attestationProviders/{providerName}'),
                    "version": "2021-06-01",
                    "subresource": "properties.attestUri",
                },
            })
            self.assertTrue(rv.status_code == 200)
            rv = c.get(f"{ws_url}/ClientConfig")
            self.assertTrue(rv.status_code == 200)
            client_config = rv.get_json()
            self.assertEqual(client_config['endpoints']['type'], 'http-operation')
            self.assertEqual(client_config['endpoints']['selector'], {'json': {'name': 'response', 'prop': {'name': 'properties.attestUri', 'type': 'simple'}, 'type': 'object'}, 'ref': '$EndpointInstance', 'var': '$Endpoint'})
            self.assertEqual(client_config['endpoints']['resource']['id'], swagger_resource_path_to_resource_id('/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Attestation/attestationProviders/{providerName}'))
            self.assertEqual(client_config['endpoints']['resource']['version'], '2021-06-01')
            self.assertEqual(client_config['endpoints']['resource']['subresource'], 'properties.attestUri')
            self.assertEqual(client_config['argGroup'], {
                'name': 'Client',
                'args': [
                    {
                        'var': '$Client.Endpoint.Path.providerName',
                        'options': ['provider-name'],
                        'required': True,
                        'type': 'string',
                        'group': 'Client',
                        'idPart': 'name',
                        'help': {'short': 'Name of the attestation provider.'},
                    },
                    {
                        'var': '$Client.Endpoint.Path.resourceGroupName',
                        'options': ['g', 'resource-group'],
                        'required': True,
                        'type': 'ResourceGroupName',
                        'group': 'Client',
                        'idPart': 'resource_group',
                    },
                    {
                        'var': '$Client.Endpoint.Path.subscriptionId',
                        'options': ['subscription'],
                        'required': True,
                        'type': 'SubscriptionId',
                        'group': 'Client',
                        'idPart': 'subscription',
                    }
                ]
            })

            # add resources
            rv = c.post(f"{ws_url}/CommandTree/Nodes/aaz/AddSwagger", json={
                'module': module,
                'version': api_version,
                'resources': [
                    {'id': swagger_resource_path_to_resource_id('/policies/{attestationType}'), 'options': {'update_by': 'None'}},
                    {'id': swagger_resource_path_to_resource_id('/policies/{attestationType}:reset')},
                    {'id': swagger_resource_path_to_resource_id('/certificates')},
                    {'id': swagger_resource_path_to_resource_id('/certificates:add')},
                    {'id': swagger_resource_path_to_resource_id('/certificates:remove')},
                ]
            })
            self.assertTrue(rv.status_code == 200)

            command_tree = rv.get_json()

            # modify command tree
            rv = c.post(f"{ws_url}/CommandTree/Nodes/aaz/attestation/policy/Leaves/create/Rename", json={
                "name": "attestation policy set"
            })
            self.assertTrue(rv.status_code == 200)
            rv = c.post(f"{ws_url}/CommandTree/Nodes/aaz/attestation/certificate/Leaves/show/Rename", json={
                "name": "attestation signer list"
            })
            self.assertTrue(rv.status_code == 200)
            rv = c.post(f"{ws_url}/CommandTree/Nodes/aaz/attestation/Leaves/certificatesadd/Rename", json={
                "name": "attestation signer add"
            })
            self.assertTrue(rv.status_code == 200)
            rv = c.post(f"{ws_url}/CommandTree/Nodes/aaz/attestation/Leaves/certificatesremove/Rename", json={
                "name": "attestation signer remove"
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.delete(f"{ws_url}/CommandTree/Nodes/aaz/attestation/certificate")
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/attestation", json={
                "help": {
                    "short": "test"
                }
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/attestation/signer", json={
                "help": {
                    "short": "test"
                }
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/attestation/policy", json={
                "help": {
                    "short": "test"
                }
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.get(f"{ws_url}/CommandTree/Nodes/aaz")
            self.assertTrue(rv.status_code == 200)
            command_tree = rv.get_json()

            rv = c.post(f"{ws_url}/Generate")
            self.assertTrue(rv.status_code == 200)

            # update client config without change
            rv = c.get(f"{ws_url}/ClientConfig")
            self.assertTrue(rv.status_code == 200)
            client_config = rv.get_json()
            old_version = client_config['version']
            rv = c.post(f"{ws_url}/ClientConfig", json={
                "auth": {
                    "aad": {
                        "scopes": ["https://attest.azure.net/.default"]
                    }
                },
                "resource": {
                    "plane": PlaneEnum.Mgmt,
                    "module": module,
                    "id": swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Attestation/attestationProviders/{providerName}'),
                    "version": "2021-06-01",
                    "subresource": "properties.attestUri",
                },
            })
            self.assertTrue(rv.status_code == 200)
            rv = c.get(f"{ws_url}/ClientConfig")
            self.assertTrue(rv.status_code == 200)
            client_config = rv.get_json()
            self.assertTrue(client_config['version'] == old_version)

            # update client config by api version changed.
            rv = c.post(f"{ws_url}/ClientConfig", json={
                "auth": {
                    "aad": {
                        "scopes": ["https://attest.azure.net/.default"]
                    }
                },
                "resource": {
                    "plane": PlaneEnum.Mgmt,
                    "module": module,
                    "id": swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Attestation/attestationProviders/{providerName}'),
                    "version": "2021-06-01-preview",
                    "subresource": "properties.attestUri",
                },
            })
            self.assertTrue(rv.status_code == 200)
            client_config = rv.get_json()
            # the client version should be updated.
            self.assertTrue(client_config['version'] != old_version)

            # update client config with invalid subresource
            rv = c.post(f"{ws_url}/ClientConfig", json={
                "auth": {
                    "aad": {
                        "scopes": ["https://attest.azure.net/.default"]
                    }
                },
                "resource": {
                    "plane": PlaneEnum.Mgmt,
                    "module": module,
                    "id": swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Attestation/attestationProviders/{providerName}'),
                    "version": "2021-06-01-preview",
                    "subresource": "property.attestUri",
                },
            })
            self.assertTrue(rv.status_code == 400)
            self.assertEqual(rv.json['message'], "Cannot find remain index ['property', 'attestUri']")

            rv = c.post(f"{ws_url}/ClientConfig", json={
                "auth": {
                    "aad": {
                        "scopes": ["https://attest.azure.net/.default"]
                    }
                },
                "resource": {
                    "plane": PlaneEnum.Mgmt,
                    "module": module,
                    "id": swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Attestation/attestationProviders/{providerName}'),
                    "version": "2021-06-01-preview",
                    "subresource": "properties.attest",
                },
            })
            self.assertTrue(rv.status_code == 400)
            self.assertEqual(rv.json['message'], "Cannot find remain index ['attest']")

            rv = c.post(f"{ws_url}/ClientConfig", json={
                "auth": {
                    "aad": {
                        "scopes": ["https://attest.azure.net/.default"]
                    }
                },
                "resource": {
                    "plane": PlaneEnum.Mgmt,
                    "module": module,
                    "id": swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Attestation/attestationProviders/{providerName}'),
                    "version": "2021-06-01-preview",
                    "subresource": "properties.attestUri.invalid",
                },
            })
            self.assertTrue(rv.status_code == 400)
            self.assertEqual(rv.json['message'], "Not support remain index ['invalid']")
