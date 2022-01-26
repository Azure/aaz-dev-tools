import json

from command.tests.common import CommandTestCase, workspace_name
from utils.plane import PlaneEnum
import os
from swagger.utils.tools import swagger_resource_path_to_resource_id


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

    @workspace_name("test_workspace_command_rename")
    def test_workspace_rename(self, ws_name):
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



