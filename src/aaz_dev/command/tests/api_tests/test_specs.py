from utils.stage import AAZStageEnum
from command.tests.common import CommandTestCase, workspace_name
from swagger.utils.tools import swagger_resource_path_to_resource_id
from utils.plane import PlaneEnum
from utils.base64 import b64encode_str


class APIAAZSpecsTest(CommandTestCase):

    @workspace_name("test_aaz_specs")
    def test_aaz_specs(self, ws_name):
        # prepare aaz
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

        # test aaz command tree
        with self.app.test_client() as c:
            rv = c.get(f"/AAZ/Specs/CommandTree/Nodes/aaz")
            self.assertTrue(rv.status_code == 200)
            command_tree = rv.get_json()
            self.assertTrue('edge-order' in command_tree['commandGroups'])

            rv = c.get(f"/AAZ/Specs/CommandTree/Nodes/aaz/edge-order")
            self.assertTrue(rv.status_code == 200)
            node = rv.get_json()
            self.assertTrue('address' in node['commandGroups'])
            self.assertTrue('list-configuration' in node['commands'])

            rv = c.get(f"/AAZ/Specs/CommandTree/Nodes/aaz/edge-order/Leaves/list-configuration")
            self.assertTrue(rv.status_code == 200)
            leaf = rv.get_json()
            self.assertTrue(leaf['names'] == ['edge-order', 'list-configuration'])
            self.assertTrue(len(leaf['versions']) == 1)

            rv = c.get(f"/AAZ/Specs/CommandTree/Nodes/aaz/edge-order/Leaves/list-configuration/Versions/{b64encode_str('2021-12-01')}")
            self.assertTrue(rv.status_code == 200)
            command_version = rv.get_json()
            self.assertTrue(command_version['names'] == ['edge-order', 'list-configuration'])
            self.assertTrue(command_version['version'] == '2021-12-01')
