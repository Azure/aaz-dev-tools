from aazdev.tests.common import ApiTestCase
from command.tests.common import workspace_name
from swagger.utils.tools import swagger_resource_path_to_resource_id
from utils.plane import PlaneEnum
from utils.stage import AAZStageEnum


class CommandTestCase(ApiTestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    # def test_prepare_aaz(self):
    #     self.prepare_aaz()

    def prepare_aaz(self):
        self.prepare_edge_order_aaz_2020_12_01_preview()
        self.prepare_edge_order_aaz_2021_12_01()
        self.prepare_databricks_aaz_2018_04_01()
        self.prepare_databricks_aaz_2021_04_01_preview()

        self.prepare_elastic_aaz_2020_07_01_preview()
        self.prepare_elastic_aaz_2020_07_01()
        self.prepare_elastic_aaz_2021_09_01_preview()
        self.prepare_elastic_aaz_2021_10_01_preview()

    @workspace_name("prepare_edge_order_aaz_2020_12_01_preview")
    def prepare_edge_order_aaz_2020_12_01_preview(self, ws_name):
        api_version = '2020-12-01-preview'
        module = 'edgeorder'
        with self.app.test_client() as c:
            rv = c.post(f"/AAZ/Editor/Workspaces", json={
                "name": ws_name + '_' + api_version,
                "plane": PlaneEnum.Mgmt,
            })
            self.assertTrue(rv.status_code == 200)
            ws = rv.get_json()
            ws_url = ws['url']
            rv = c.post(f"{ws_url}/CommandTree/Nodes/aaz/AddSwagger", json={
                'module': module,
                'version': api_version,
                'resources': [
                    # TODO: bellow three resources need to support discriminator in command generation
                    # swagger_resource_path_to_resource_id(
                    #     '/subscriptions/{subscriptionId}/providers/Microsoft.EdgeOrder/listProductFamilies'),
                    # swagger_resource_path_to_resource_id(
                    #     '/subscriptions/{subscriptionId}/providers/Microsoft.EdgeOrder/listConfigurations'),
                    # swagger_resource_path_to_resource_id(
                    #     '/subscriptions/{subscriptionId}/providers/Microsoft.EdgeOrder/productFamiliesMetadata'),

                    {'id': swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/providers/Microsoft.EdgeOrder/addresses')},
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
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.EdgeOrder/orderItems/{orderItemName}'),
                        "options": {"update_by": "PatchOnly"}},
                    {'id': swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.EdgeOrder/orderItems/{orderItemName}/cancel')},
                    {'id': swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.EdgeOrder/orderItems/{orderItemName}/return')},
                ]
            })
            self.assertTrue(rv.status_code == 200)

            # rv = c.post(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/Leaves/list-configuration/Rename", json={
            #     'name': "edge-order list-config"
            # })
            # self.assertTrue(rv.status_code == 200)
            #
            # rv = c.post(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/Leaves/list-product-family/Rename", json={
            #     'name': "edge-order list-family"
            # })
            # self.assertTrue(rv.status_code == 200)
            #
            # rv = c.post(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/Leaves/product-families-metadatum/Rename", json={
            #     'name': "edge-order list-metadata"
            # })
            # self.assertTrue(rv.status_code == 200)

            rv = c.get(f"{ws_url}/CommandTree/Nodes/aaz")
            self.assertTrue(rv.status_code == 200)
            command_tree = rv.get_json()

            # rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/Leaves/list-config", json={
            #     "help": {
            #         "short": "Get an order.",
            #     },
            #     "examples": [{
            #         "name": "GetOrderByName",
            #         "commands": [
            #             'edge-order list-config --configuration-filters'
            #         ]
            #     }]
            # })
            # self.assertTrue(rv.status_code == 200)
            #
            # rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/Leaves/list-family", json={
            #     "help": {
            #         "short": "This method provides the list of product families for the given subscription.",
            #     },
            #     "examples": [{
            #         "name": "ListProductFamilies",
            #         "commands": [
            #             'edge-order edgeorder list-family --filterable-properties {azurestackedge:{type:ShipToCountries, supportedValues:[US]}}'
            #         ]
            #     }]
            # })
            # self.assertTrue(rv.status_code == 200)
            #
            # rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/Leaves/list-metadata", json={
            #     "help": {
            #         "short": "This method provides the list of product families metadata for the given subscription.",
            #     },
            #     "examples": [{
            #         "name": "ListProductFamiliesMetadata",
            #         "commands": [
            #             'edge-order list-metadata'
            #         ]
            #     }]
            # })
            # self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/edge-order", json={
                "help": {
                    "short": "Manage Edge Order.",
                },
                "stage": AAZStageEnum.Preview
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/order", json={
                "help": {
                    "short": "Manage order with Edge Order.",
                },
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/order/Leaves/show", json={
                "help": {
                    "short": "Get an order.",
                },
                "examples": [{
                    "name": "GetOrderByName",
                    "commands": [
                        'edge-order order show --location "TestLocation" --name "TestOrderItemName901" --resource-group "TestRG"'
                    ]
                }]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/address", json={
                "help": {
                    "short": "Manage address with Edge Order.",
                }
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/address/Leaves/list", json={
                "help": {
                    "short": "List all the addresses available under the given resource group. And List all the addresses available under the subscription.",
                },
                "examples": [{
                    "name": "ListAddressesAtResourceGroupLevel",
                    "commands": [
                        'edge-order address list --resource-group "TestRG"'
                    ]
                }, {
                    "name": "ListAddressesAtSubscriptionLevel",
                    "commands": [
                        'edge-order address list'
                    ]
                }]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/address/Leaves/show", json={
                "help": {
                    "short": "Get information about the specified address.",
                },
                "examples": [{
                    "name": "GetAddressByName",
                    "commands": [
                        'edge-order address show --name "TestMSAddressName" --resource-group "TestRG"'
                    ]
                }]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/address/Leaves/create", json={
                "help": {
                    "short": "Create a new address with the specified parameters. Existing address can be updated with this API.",
                },
                "examples": [{
                    "name": "CreateAddress",
                    "commands": [
                        'edge-order address create --name "TestMSAddressName" --location "eastus" --contact-details {contact-name:\'Petr Cech\',email-list:testemail@microsoft.com,phone:1234567890,phone-extension:''} --shipping-address {address-type:\'None\',city:\'San Francisco\',company-name:Microsoft,country:US,postal-code:94107,state-or-province:CA,street-address1:\'16 TOWNSEND ST\',street-address2:\'UNIT 1\'} --resource-group TestRG'
                    ]
                }]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/address/Leaves/update", json={
                "help": {
                    "short": "Update the properties of an existing address.",
                },
                "examples": [{
                    "name": "UpdateAddress",
                    "commands": [
                        'edge-order address update --name "TestMSAddressName" --location "eastus" --resource-group TestRG --contact-details contact-name=\'Petr Cech\''
                    ]
                }]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/address/Leaves/delete", json={
                "help": {
                    "short": "Delete an address.",
                },
                "examples": [{
                    "name": "DeleteAddressByName",
                    "commands": [
                        'edge-order address delete --name "TestAddressName1" --resource-group "TestRG"'
                    ]
                }]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/order/Leaves/list", json={
                "help": {
                    "short": "List order at resource group level. And List order at subscription level.",
                },
                "examples": [{
                    "name": "ListOrderAtResourceGroupLevel",
                    "commands": [
                        'edge-order order list --resource-group "TestRG"'
                    ]
                }]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/order-item", json={
                "help": {
                    "short": "Manage order item with edge order.",
                },
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/order-item/Leaves/list", json={
                "help": {
                    "short": "List order at resource group level. And List order at subscription level.",
                },
                "examples": [{
                    "name": "ListOrderItemsAtResourceGroupLevel",
                    "commands": [
                        'edge-order order-item list --resource-group "TestRG"'
                    ]
                }, {
                    "name": "ListOrderItemsAtSubscriptionLevel",
                    "commands": [
                        'edge-order order-item list'
                    ]
                }]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/order-item/Leaves/show", json={
                "help": {
                    "short": "Get an order item.",
                },
                "examples": [{
                    "name": "GetOrderItemByName",
                    "commands": [
                        'edge-order order-item show --name "TestOrderItemName01" --resource-group "TestRG"'
                    ]
                }]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/order-item/Leaves/create", json={
                "help": {
                    "short": "Create an order item.",
                },
                "examples": [{
                    "name": "GetOrderItemByName",
                    "commands": [
                        'edge-order order-item create --name "TestOrderItemName01" --resource-group "TestRG"'
                    ]
                }]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/order-item/Leaves/update", json={
                "help": {
                    "short": "Update the properties of an existing order item.",
                },
                "examples": [{
                    "name": "GetOrderItemByName",
                    "commands": [
                        'edge-order order-item update --name "TestOrderItemName01" --resource-group "TestRG" --contact-details contact-name=\'Updated contact name\''
                    ]
                }]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/order-item/Leaves/delete", json={
                "help": {
                    "short": "Delete an order item.",
                },
                "examples": [{
                    "name": "DeleteOrderItemByName",
                    "commands": [
                        'edge-order order-item delete --name "TestOrderItemName01" --resource-group "TestRG"'
                    ]
                }]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/order-item/Leaves/cancel", json={
                "help": {
                    "short": "Cancel order item.",
                },
                "examples": [{
                    "name": "CancelOrderItem",
                    "commands": [
                        'edge-order order-item cancel --reason "Order cancelled" --name "TestOrderItemName1" --resource-group "TestRG"'
                    ]
                }]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/order-item/Leaves/return", json={
                "help": {
                    "short": "Return order item.",
                },
                "examples": [{
                    "name": "ReturnOrderItem",
                    "commands": [
                        'edge-order order-item return --name "TestOrderName1" --resource-group "TestRG" --return-reason "Order returned"'
                    ]
                }]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.post(f"{ws_url}/Generate")
            self.assertTrue(rv.status_code == 200)

    @workspace_name("prepare_edge_order_aaz_2021_12_01")
    def prepare_edge_order_aaz_2021_12_01(self, ws_name):
        api_version = '2021-12-01'
        module = 'edgeorder'
        with self.app.test_client() as c:
            rv = c.post(f"/AAZ/Editor/Workspaces", json={
                "name": ws_name + '_' + api_version,
                "plane": PlaneEnum.Mgmt,
            })
            self.assertTrue(rv.status_code == 200)
            ws = rv.get_json()
            ws_url = ws['url']
            rv = c.post(f"{ws_url}/CommandTree/Nodes/aaz/AddSwagger", json={
                'module': module,
                'version': api_version,
                'resources': [
                    # TODO: bellow three resources need to support discriminator in command generation
                    # swagger_resource_path_to_resource_id(
                    #     '/subscriptions/{subscriptionId}/providers/Microsoft.EdgeOrder/listProductFamilies'),
                    # swagger_resource_path_to_resource_id(
                    #     '/subscriptions/{subscriptionId}/providers/Microsoft.EdgeOrder/listConfigurations'),
                    # swagger_resource_path_to_resource_id(
                    #     '/subscriptions/{subscriptionId}/providers/Microsoft.EdgeOrder/productFamiliesMetadata'),

                    {'id': swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/providers/Microsoft.EdgeOrder/addresses')},
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
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.EdgeOrder/orderItems/{orderItemName}'),
                        "options": {"update_by": "PatchOnly"}},
                    {'id': swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.EdgeOrder/orderItems/{orderItemName}/cancel')},
                    {'id': swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.EdgeOrder/orderItems/{orderItemName}/return')},
                ]
            })
            self.assertTrue(rv.status_code == 200)

            # rv = c.post(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/Leaves/list-configuration/Rename", json={
            #     'name': "edge-order list-config"
            # })
            # self.assertTrue(rv.status_code == 200)
            #
            # rv = c.post(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/Leaves/list-product-family/Rename", json={
            #     'name': "edge-order list-family"
            # })
            # self.assertTrue(rv.status_code == 200)
            #
            # rv = c.post(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/Leaves/product-families-metadatum/Rename", json={
            #     'name': "edge-order list-metadata"
            # })
            # self.assertTrue(rv.status_code == 200)

            rv = c.get(f"{ws_url}/CommandTree/Nodes/aaz")
            self.assertTrue(rv.status_code == 200)
            command_tree = rv.get_json()

            # rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/Leaves/list-config", json={
            #     "help": {
            #         "short": "Get an order.",
            #     },
            #     "examples": [{
            #         "name": "GetOrderByName",
            #         "commands": [
            #             'edge-order list-config --configuration-filters'
            #         ]
            #     }]
            # })
            # self.assertTrue(rv.status_code == 200)
            #
            # rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/Leaves/list-family", json={
            #     "help": {
            #         "short": "This method provides the list of product families for the given subscription.",
            #     },
            #     "examples": [{
            #         "name": "ListProductFamilies",
            #         "commands": [
            #             'edge-order edgeorder list-family --filterable-properties {azurestackedge:{type:ShipToCountries, supportedValues:[US]}}'
            #         ]
            #     }]
            # })
            # self.assertTrue(rv.status_code == 200)
            #
            # rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/Leaves/list-metadata", json={
            #     "help": {
            #         "short": "This method provides the list of product families metadata for the given subscription.",
            #     },
            #     "examples": [{
            #         "name": "ListProductFamiliesMetadata",
            #         "commands": [
            #             'edge-order list-metadata'
            #         ]
            #     }]
            # })
            # self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/edge-order", json={
                "help": {
                    "short": "Manage Edge Order.",
                },
                "stage": AAZStageEnum.Stable
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/order", json={
                "help": {
                    "short": "Manage order with Edge Order.",
                },
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/order/Leaves/show", json={
                "help": {
                    "short": "Get an order.",
                },
                "examples": [{
                    "name": "GetOrderByName",
                    "commands": [
                        'edge-order order show --location "TestLocation" --name "TestOrderItemName901" --resource-group "TestRG"'
                    ]
                }]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/address", json={
                "help": {
                    "short": "Manage address with Edge Order.",
                }
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/address/Leaves/list", json={
                "help": {
                    "short": "List all the addresses available under the given resource group. And List all the addresses available under the subscription.",
                },
                "examples": [{
                    "name": "ListAddressesAtResourceGroupLevel",
                    "commands": [
                        'edge-order address list --resource-group "TestRG"'
                    ]
                }, {
                    "name": "ListAddressesAtSubscriptionLevel",
                    "commands": [
                        'edge-order address list'
                    ]
                }]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/address/Leaves/show", json={
                "help": {
                    "short": "Get information about the specified address.",
                },
                "examples": [{
                    "name": "GetAddressByName",
                    "commands": [
                        'edge-order address show --name "TestMSAddressName" --resource-group "TestRG"'
                    ]
                }]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/address/Leaves/create", json={
                "help": {
                    "short": "Create a new address with the specified parameters. Existing address can be updated with this API.",
                },
                "examples": [{
                    "name": "CreateAddress",
                    "commands": [
                        'edge-order address create --name "TestMSAddressName" --location "eastus" --contact-details {contact-name:\'Petr Cech\',email-list:testemail@microsoft.com,phone:1234567890,phone-extension:''} --shipping-address {address-type:\'None\',city:\'San Francisco\',company-name:Microsoft,country:US,postal-code:94107,state-or-province:CA,street-address1:\'16 TOWNSEND ST\',street-address2:\'UNIT 1\'} --resource-group TestRG'
                    ]
                }]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/address/Leaves/update", json={
                "help": {
                    "short": "Update the properties of an existing address.",
                },
                "examples": [{
                    "name": "UpdateAddress",
                    "commands": [
                        'edge-order address update --name "TestMSAddressName" --location "eastus" --resource-group TestRG --contact-details contact-name=\'Petr Cech\''
                    ]
                }]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/address/Leaves/delete", json={
                "help": {
                    "short": "Delete an address.",
                },
                "examples": [{
                    "name": "DeleteAddressByName",
                    "commands": [
                        'edge-order address delete --name "TestAddressName1" --resource-group "TestRG"'
                    ]
                }]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/order/Leaves/list", json={
                "help": {
                    "short": "List order at resource group level. And List order at subscription level.",
                },
                "examples": [{
                    "name": "ListOrderAtResourceGroupLevel",
                    "commands": [
                        'edge-order order list --resource-group "TestRG"'
                    ]
                }]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/order-item", json={
                "help": {
                    "short": "Manage order item with edge order.",
                },
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/order-item/Leaves/list", json={
                "help": {
                    "short": "List order at resource group level. And List order at subscription level.",
                },
                "examples": [{
                    "name": "ListOrderItemsAtResourceGroupLevel",
                    "commands": [
                        'edge-order order-item list --resource-group "TestRG"'
                    ]
                }, {
                    "name": "ListOrderItemsAtSubscriptionLevel",
                    "commands": [
                        'edge-order order-item list'
                    ]
                }]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/order-item/Leaves/show", json={
                "help": {
                    "short": "Get an order item.",
                },
                "examples": [{
                    "name": "GetOrderItemByName",
                    "commands": [
                        'edge-order order-item show --name "TestOrderItemName01" --resource-group "TestRG"'
                    ]
                }]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/order-item/Leaves/create", json={
                "help": {
                    "short": "Create an order item.",
                },
                "examples": [{
                    "name": "GetOrderItemByName",
                    "commands": [
                        'edge-order order-item create --name "TestOrderItemName01" --resource-group "TestRG"'
                    ]
                }]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/order-item/Leaves/update", json={
                "help": {
                    "short": "Update the properties of an existing order item.",
                },
                "examples": [{
                    "name": "GetOrderItemByName",
                    "commands": [
                        'edge-order order-item update --name "TestOrderItemName01" --resource-group "TestRG" --contact-details contact-name=\'Updated contact name\''
                    ]
                }]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/order-item/Leaves/delete", json={
                "help": {
                    "short": "Delete an order item.",
                },
                "examples": [{
                    "name": "DeleteOrderItemByName",
                    "commands": [
                        'edge-order order-item delete --name "TestOrderItemName01" --resource-group "TestRG"'
                    ]
                }]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/order-item/Leaves/cancel", json={
                "help": {
                    "short": "Cancel order item.",
                },
                "examples": [{
                    "name": "CancelOrderItem",
                    "commands": [
                        'edge-order order-item cancel --reason "Order cancelled" --name "TestOrderItemName1" --resource-group "TestRG"'
                    ]
                }]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/edge-order/order-item/Leaves/return", json={
                "help": {
                    "short": "Return order item.",
                },
                "examples": [{
                    "name": "ReturnOrderItem",
                    "commands": [
                        'edge-order order-item return --name "TestOrderName1" --resource-group "TestRG" --return-reason "Order returned"'
                    ]
                }]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.post(f"{ws_url}/Generate")
            self.assertTrue(rv.status_code == 200)

    @workspace_name("prepare_databricks_aaz_2018_04_01")
    def prepare_databricks_aaz_2018_04_01(self, ws_name):
        api_version = '2018-04-01'
        module = 'databricks'
        with self.app.test_client() as c:
            rv = c.post(f"/AAZ/Editor/Workspaces", json={
                "name": ws_name,
                "plane": PlaneEnum.Mgmt,
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

            rv = c.get(f"{ws_url}/CommandTree/Nodes/aaz")
            self.assertTrue(rv.status_code == 200)
            command_tree = rv.get_json()

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/data-bricks", json={
                "help": {
                    "short": "Manage databricks workspaces.",
                },
                "stage": AAZStageEnum.Stable
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/data-bricks/workspace", json={
                "help": {
                    "short": "Commands to manage databricks workspace.",
                },
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/data-bricks/workspace/Leaves/create", json={
                "help": {
                    "short": "Create a new workspace.",
                },
                "examples": [
                    {
                        "name": "Create a workspace",
                        "commands": [
                            "data-bricks workspace create --resource-group MyResourceGroup --name MyWorkspace --location westus --sku standard"
                        ]
                    },
                    {
                        "name": "Create a workspace with managed identity for storage account",
                        "commands": [
                            "data-bricks workspace create --resource-group MyResourceGroup --name MyWorkspace --location eastus2euap --sku premium --prepare-encryption"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/data-bricks/workspace/Leaves/update", json={
                "help": {
                    "short": "Update the workspace.",
                },
                "examples": [
                    {
                        "name": "Update the workspace's tags.",
                        "commands": [
                            "data-bricks workspace update --resource-group MyResourceGroup --name MyWorkspace --tags {key1:value1,key2:value2}"
                        ]
                    },
                    {
                        "name": "Clean the workspace's tags.",
                        "commands": [
                            "data-bricks workspace update --resource-group MyResourceGroup --name MyWorkspace --tags {}"
                        ]
                    },
                    {
                        "name": "Prepare for CMK encryption by assigning identity for storage account.",
                        "commands": [
                            "data-bricks workspace update --resource-group MyResourceGroup --name MyWorkspace --prepare-encryption"
                        ]
                    },
                    {
                        "name": "Configure CMK encryption.",
                        "commands": [
                            "data-bricks workspace update --resource-group MyResourceGroup --name MyWorkspace --key-source Microsoft.KeyVault -key-name MyKey --key-vault https://myKeyVault.vault.azure.net/ --key-version 00000000000000000000000000000000"
                        ]
                    },
                    {
                        "name": "Revert encryption to Microsoft Managed Keys.",
                        "commands": [
                            "data-bricks workspace update --resource-group MyResourceGroup --name MyWorkspace --key-source Default"
                        ]
                    },
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/data-bricks/workspace/Leaves/delete", json={
                "help": {
                    "short": "Delete the workspace.",
                },
                "examples": [
                    {
                        "name": "Delete the workspace.",
                        "commands": [
                            "data-bricks workspace delete --resource-group MyResourceGroup --name MyWorkspace"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/data-bricks/workspace/Leaves/show", json={
                "help": {
                    "short": "Show the workspace.",
                },
                "examples": [
                    {
                        "name": "Show the workspace.",
                        "commands": [
                            "data-bricks workspace show --resource-group MyResourceGroup --name MyWorkspace"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/data-bricks/workspace/Leaves/list", json={
                "help": {
                    "short": "Get all the workspaces.",
                },
                "examples": [
                    {
                        "name": "List workspaces within a resource group.",
                        "commands": [
                            "data-bricks workspace list --resource-group MyResourceGroup"
                        ]
                    },
                    {
                        "name": "List workspaces within the default subscription.",
                        "commands": [
                            "data-bricks workspace list"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/data-bricks/workspace/vnet-peering", json={
                "help": {
                    "short": "Commands to manage databricks workspace vnet peering.",
                },
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/data-bricks/workspace/vnet-peering/Leaves/create", json={
                "help": {
                    "short": "Create a vnet peering for a workspace.",
                },
                "examples": [
                    {
                        "name": "Create a vnet peering for a workspace",
                        "commands": [
                            "data-bricks workspace vnet-peering create --resource-group MyResourceGroup --workspace-name MyWorkspace -n MyPeering --remote-vnet /subscriptions/000000-0000-0000/resourceGroups/MyRG/providers/Microsoft.Network/virtualNetworks/MyVNet"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/data-bricks/workspace/vnet-peering/Leaves/update", json={
                "help": {
                    "short": "Update the vnet peering.",
                },
                "examples": [
                    {
                        "name": "Update the vnet peering (enable gateway transit and disable virtual network access).",
                        "commands": [
                            "data-bricks workspace vnet-peering update --resource-group MyResourceGroup --workspace-name MyWorkspace -n MyPeering --allow-gateway-transit --allow-virtual-network-access false",
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/data-bricks/workspace/vnet-peering/Leaves/list", json={
                "help": {
                    "short": "List vnet peerings under a workspace.",
                },
                "examples": [
                    {
                        "name": "List vnet peerings under a workspace.",
                        "commands": [
                            "data-bricks workspace vnet-peering list --resource-group MyResourceGroup --workspace-name MyWorkspace",
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/data-bricks/workspace/vnet-peering/Leaves/delete", json={
                "help": {
                    "short": "Delete the vnet peering.",
                },
                "examples": [
                    {
                        "name": "Delete the vnet peering.",
                        "commands": [
                            "data-bricks workspace vnet-peering delete --resource-group MyResourceGroup --workspace-name MyWorkspace -n MyPeering",
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/data-bricks/workspace/vnet-peering/Leaves/show", json={
                "help": {
                    "short": "Show the vnet peering.",
                },
                "examples": [
                    {
                        "name": "Show the vnet peering.",
                        "commands": [
                            "data-bricks workspace vnet-peering show --resource-group MyResourceGroup --workspace-name MyWorkspace -n MyPeering",
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.post(f"{ws_url}/Generate")
            self.assertTrue(rv.status_code == 200)

    @workspace_name("prepare_databricks_aaz_2021_04_01_preview")
    def prepare_databricks_aaz_2021_04_01_preview(self, ws_name):
        api_version = '2021-04-01-preview'
        module = 'databricks'
        with self.app.test_client() as c:
            rv = c.post(f"/AAZ/Editor/Workspaces", json={
                "name": ws_name,
                "plane": PlaneEnum.Mgmt,
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

            rv = c.get(f"{ws_url}/CommandTree/Nodes/aaz")
            self.assertTrue(rv.status_code == 200)
            command_tree = rv.get_json()

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/data-bricks", json={
                "help": {
                    "short": "Manage databricks workspaces.",
                },
                "stage": AAZStageEnum.Preview
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/data-bricks/workspace", json={
                "help": {
                    "short": "Commands to manage databricks workspace.",
                },
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/data-bricks/workspace/Leaves/create", json={
                "help": {
                    "short": "Create a new workspace.",
                },
                "examples": [
                    {
                        "name": "Create a workspace",
                        "commands": [
                            "data-bricks workspace create --resource-group MyResourceGroup --name MyWorkspace --location westus --sku standard"
                        ]
                    },
                    {
                        "name": "Create a workspace with managed identity for storage account",
                        "commands": [
                            "data-bricks workspace create --resource-group MyResourceGroup --name MyWorkspace --location eastus2euap --sku premium --prepare-encryption"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/data-bricks/workspace/Leaves/update", json={
                "help": {
                    "short": "Update the workspace.",
                },
                "examples": [
                    {
                        "name": "Update the workspace's tags.",
                        "commands": [
                            "data-bricks workspace update --resource-group MyResourceGroup --name MyWorkspace --tags {key1:value1,key2:value2}"
                        ]
                    },
                    {
                        "name": "Clean the workspace's tags.",
                        "commands": [
                            "data-bricks workspace update --resource-group MyResourceGroup --name MyWorkspace --tags {}"
                        ]
                    },
                    {
                        "name": "Prepare for CMK encryption by assigning identity for storage account.",
                        "commands": [
                            "data-bricks workspace update --resource-group MyResourceGroup --name MyWorkspace --prepare-encryption"
                        ]
                    },
                    {
                        "name": "Configure CMK encryption.",
                        "commands": [
                            "data-bricks workspace update --resource-group MyResourceGroup --name MyWorkspace --key-source Microsoft.KeyVault -key-name MyKey --key-vault https://myKeyVault.vault.azure.net/ --key-version 00000000000000000000000000000000"
                        ]
                    },
                    {
                        "name": "Revert encryption to Microsoft Managed Keys.",
                        "commands": [
                            "data-bricks workspace update --resource-group MyResourceGroup --name MyWorkspace --key-source Default"
                        ]
                    },
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/data-bricks/workspace/Leaves/delete", json={
                "help": {
                    "short": "Delete the workspace.",
                },
                "examples": [
                    {
                        "name": "Delete the workspace.",
                        "commands": [
                            "data-bricks workspace delete --resource-group MyResourceGroup --name MyWorkspace"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/data-bricks/workspace/Leaves/show", json={
                "help": {
                    "short": "Show the workspace.",
                },
                "examples": [
                    {
                        "name": "Show the workspace.",
                        "commands": [
                            "data-bricks workspace show --resource-group MyResourceGroup --name MyWorkspace"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/data-bricks/workspace/Leaves/list", json={
                "help": {
                    "short": "Get all the workspaces.",
                },
                "examples": [
                    {
                        "name": "List workspaces within a resource group.",
                        "commands": [
                            "data-bricks workspace list --resource-group MyResourceGroup"
                        ]
                    },
                    {
                        "name": "List workspaces within the default subscription.",
                        "commands": [
                            "data-bricks workspace list"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/data-bricks/workspace/vnet-peering", json={
                "help": {
                    "short": "Commands to manage databricks workspace vnet peering.",
                },
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/data-bricks/workspace/vnet-peering/Leaves/create", json={
                "help": {
                    "short": "Create a vnet peering for a workspace.",
                },
                "examples": [
                    {
                        "name": "Create a vnet peering for a workspace",
                        "commands": [
                            "data-bricks workspace vnet-peering create --resource-group MyResourceGroup --workspace-name MyWorkspace -n MyPeering --remote-vnet /subscriptions/000000-0000-0000/resourceGroups/MyRG/providers/Microsoft.Network/virtualNetworks/MyVNet"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/data-bricks/workspace/vnet-peering/Leaves/update", json={
                "help": {
                    "short": "Update the vnet peering.",
                },
                "examples": [
                    {
                        "name": "Update the vnet peering (enable gateway transit and disable virtual network access).",
                        "commands": [
                            "data-bricks workspace vnet-peering update --resource-group MyResourceGroup --workspace-name MyWorkspace -n MyPeering --allow-gateway-transit --allow-virtual-network-access false",
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/data-bricks/workspace/vnet-peering/Leaves/list", json={
                "help": {
                    "short": "List vnet peerings under a workspace.",
                },
                "examples": [
                    {
                        "name": "List vnet peerings under a workspace.",
                        "commands": [
                            "data-bricks workspace vnet-peering list --resource-group MyResourceGroup --workspace-name MyWorkspace",
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/data-bricks/workspace/vnet-peering/Leaves/delete", json={
                "help": {
                    "short": "Delete the vnet peering.",
                },
                "examples": [
                    {
                        "name": "Delete the vnet peering.",
                        "commands": [
                            "data-bricks workspace vnet-peering delete --resource-group MyResourceGroup --workspace-name MyWorkspace -n MyPeering",
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/data-bricks/workspace/vnet-peering/Leaves/show", json={
                "help": {
                    "short": "Show the vnet peering.",
                },
                "examples": [
                    {
                        "name": "Show the vnet peering.",
                        "commands": [
                            "data-bricks workspace vnet-peering show --resource-group MyResourceGroup --workspace-name MyWorkspace -n MyPeering",
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.post(f"{ws_url}/Generate")
            self.assertTrue(rv.status_code == 200)

    @workspace_name("prepare_elastic_aaz_2020_07_01")
    def prepare_elastic_aaz_2020_07_01(self, ws_name):
        api_version = '2020-07-01'
        module = 'elastic'
        with self.app.test_client() as c:
            rv = c.post(f"/AAZ/Editor/Workspaces", json={
                "name": ws_name,
                "plane": PlaneEnum.Mgmt,
            })
            self.assertTrue(rv.status_code == 200)
            ws = rv.get_json()
            ws_url = ws['url']
            rv = c.post(f"{ws_url}/CommandTree/Nodes/aaz/AddSwagger", json={
                'module': module,
                'version': api_version,
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

            rv = c.post(f"{ws_url}/CommandTree/Nodes/aaz/elastic/monitor/Rename", json={
                'name': "elastic-monitor"
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.delete(f"{ws_url}/CommandTree/Nodes/aaz/elastic", json={
                'name': "elastic-monitor"
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.post(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/Leaves/list-monitored-resource/Rename", json={
                'name': "elastic-monitor list-resource"
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.post(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/Leaves/vm-collection-update/Rename", json={
                'name': "elastic-monitor update-vm-collection"
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.post(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/Leaves/vm-ingestion-detail/Rename", json={
                'name': "elastic-monitor list-vm-ingestion-detail"
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.get(f"{ws_url}/CommandTree/Nodes/aaz")
            self.assertTrue(rv.status_code == 200)
            command_tree = rv.get_json()

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor", json={
                "help": {
                    "short": "Manage monitor with Elastic.",
                },
                "stage": AAZStageEnum.Stable
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/tag-rule", json={
                "help": {
                    "short": "Manage tag rule with Elastic.",
                },
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/Leaves/list", json={
                "help": {
                    "short": "List all monitors under the specified resource group. "
                             "And List all monitors under the specified subscription.",
                },
                "examples": [
                    {
                        "name": "Monitors List By ResourceGroup",
                        "commands": [
                            "elastic-monitor list --resource-group myResourceGroup"
                        ]
                    },
                    {
                        "name": "Monitors List",
                        "commands": [
                            "elastic-monitor list"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/Leaves/show", json={
                "help": {
                    "short": "Get the properties of a specific monitor resource.",
                },
                "examples": [
                    {
                        "name": "Monitors Get",
                        "commands": [
                            "elastic-monitor show --name myMonitor --resource-group myResourceGroup"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/Leaves/create", json={
                "help": {
                    "short": "Create a monitor resource.",
                },
                "examples": [
                    {
                        "name": "Monitors Create",
                        "commands": [
                            "elastic-monitor create --name myMonitor --location westus2"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/Leaves/update", json={
                "help": {
                    "short": "Update a monitor resource.",
                },
                "examples": [
                    {
                        "name": "Monitors Update",
                        "commands": [
                            "elastic-monitor update --name myMonitor --tags Environment=dev --resource-group myResourceGroup"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/Leaves/delete", json={
                "help": {
                    "short": "Delete a monitor resource.",
                },
                "examples": [
                    {
                        "name": "Monitors Delete",
                        "commands": [
                            "elastic-monitor delete --name myMonitor --resource-group myResourceGroup"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/Leaves/list-deployment-info", json={
                "help": {
                    "short": "Fetch information regarding Elastic cloud deployment corresponding to the Elastic monitor resource.",
                },
                "examples": [
                    {
                        "name": "DeploymentInfo List",
                        "commands": [
                            "elastic-monitor list-deployment-info --name myMonitor --resource-group myResourceGroup"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/Leaves/list-resource", json={
                "help": {
                    "short": "List the resources currently being monitored by the Elastic monitor resource.",
                },
                "examples": [
                    {
                        "name": "MonitoredResources List",
                        "commands": [
                            "elastic-monitor list-resource --name myMonitor --resource-group myResourceGroup"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/Leaves/list-vm-host", json={
                "help": {
                    "short": "List the vm resources currently being monitored by the Elastic monitor resource.",
                },
                "examples": [
                    {
                        "name": "VMHost List",
                        "commands": [
                            "elastic-monitor list-vm-host --name myMonitor --resource-group myResourceGroup"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/Leaves/list-vm-ingestion-detail", json={
                "help": {
                    "short": "List the vm ingestion details that will be monitored by the Elastic monitor resource.",
                },
                "examples": [
                    {
                        "name": "VMIngestion Details",
                        "commands": [
                            "elastic-monitor list-vm-ingestion-detail --name myMonitor --resource-group myResourceGroup"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/Leaves/update-vm-collection", json={
                "help": {
                    "short": "Update the vm details that will be monitored by the Elastic monitor resource.",
                },
                "examples": [
                    {
                        "name": "VMCollection Update",
                        "commands": [
                            "elastic-monitor update-vm-collection --name myMonitor --resource-group myResourceGroup "
                            "--operation-name Add --vm-resource-id /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/myResourceGroup/providers/Microsoft.Compute/virtualmachines/myVM"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/tag-rule/Leaves/list", json={
                "help": {
                    "short": "List the tag rules for a given monitor resource.",
                },
                "examples": [
                    {
                        "name": "TagRules List",
                        "commands": [
                            "elastic-monitor tag-rule list --monitor-name myMonitor --resource-group myResourceGroup"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/tag-rule/Leaves/show", json={
                "help": {
                    "short": "Get a tag rule set for a given monitor resource.",
                },
                "examples": [
                    {
                        "name": "TagRules Get",
                        "commands": [
                            "elastic-monitor tag-rule show --monitor-name myMonitor --resource-group myResourceGroup --rule-set-name default"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/tag-rule/Leaves/create", json={
                "help": {
                    "short": "Create a tag rule set for a given monitor resource.",
                },
                "examples": [
                    {
                        "name": "TagRules Create",
                        "commands": [
                            "elastic-monitor tag-rule create --monitor-name myMonitor --resource-group myResourceGroup "
                            "--rule-set-name default --filtering-tags name=Environment action=Include value=Prod "
                            "--send-aad-logs False --send-activity-logs --send-subscription-logs "
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/tag-rule/Leaves/update", json={
                "help": {
                    "short": "Update a tag rule set for a given monitor resource.",
                },
                "examples": [
                    {
                        "name": "TagRules Update",
                        "commands": [
                            "elastic-monitor tag-rule update --monitor-name myMonitor --resource-group myResourceGroup "
                            "--rule-set-name default --send-aad-logs True"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/tag-rule/Leaves/delete", json={
                "help": {
                    "short": "Delete a tag rule set for a given monitor resource.",
                },
                "examples": [
                    {
                        "name": "TagRules Delete",
                        "commands": [
                            "elastic-monitor tag-rule delete --monitor-name myMonitor --resource-group myResourceGroup "
                            "--rule-set-name default"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.post(f"{ws_url}/Generate")
            self.assertTrue(rv.status_code == 200)

    @workspace_name("prepare_elastic_aaz_2020_07_01_preview")
    def prepare_elastic_aaz_2020_07_01_preview(self, ws_name):
        api_version = '2020-07-01-preview'
        module = 'elastic'
        with self.app.test_client() as c:
            rv = c.post(f"/AAZ/Editor/Workspaces", json={
                "name": ws_name,
                "plane": PlaneEnum.Mgmt,
            })
            self.assertTrue(rv.status_code == 200)
            ws = rv.get_json()
            ws_url = ws['url']
            rv = c.post(f"{ws_url}/CommandTree/Nodes/aaz/AddSwagger", json={
                'module': module,
                'version': api_version,
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

            rv = c.post(f"{ws_url}/CommandTree/Nodes/aaz/elastic/monitor/Rename", json={
                'name': "elastic-monitor"
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.delete(f"{ws_url}/CommandTree/Nodes/aaz/elastic", json={
                'name': "elastic-monitor"
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.post(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/Leaves/list-monitored-resource/Rename", json={
                'name': "elastic-monitor list-resource"
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.post(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/Leaves/vm-collection-update/Rename", json={
                'name': "elastic-monitor update-vm-collection"
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.post(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/Leaves/vm-ingestion-detail/Rename", json={
                'name': "elastic-monitor list-vm-ingestion-detail"
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.get(f"{ws_url}/CommandTree/Nodes/aaz")
            self.assertTrue(rv.status_code == 200)
            command_tree = rv.get_json()

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor", json={
                "help": {
                    "short": "Manage monitor with Elastic.",
                },
                "stage": AAZStageEnum.Experimental
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/tag-rule", json={
                "help": {
                    "short": "Manage tag rule with Elastic.",
                },
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/Leaves/list", json={
                "help": {
                    "short": "List all monitors under the specified resource group. "
                             "And List all monitors under the specified subscription.",
                },
                "examples": [
                    {
                        "name": "Monitors List By ResourceGroup",
                        "commands": [
                            "elastic-monitor list --resource-group myResourceGroup"
                        ]
                    },
                    {
                        "name": "Monitors List",
                        "commands": [
                            "elastic-monitor list"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/Leaves/show", json={
                "help": {
                    "short": "Get the properties of a specific monitor resource.",
                },
                "examples": [
                    {
                        "name": "Monitors Get",
                        "commands": [
                            "elastic-monitor show --name myMonitor --resource-group myResourceGroup"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/Leaves/create", json={
                "help": {
                    "short": "Create a monitor resource.",
                },
                "examples": [
                    {
                        "name": "Monitors Create",
                        "commands": [
                            "elastic-monitor create --name myMonitor --location westus2"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/Leaves/update", json={
                "help": {
                    "short": "Update a monitor resource.",
                },
                "examples": [
                    {
                        "name": "Monitors Update",
                        "commands": [
                            "elastic-monitor update --name myMonitor --tags Environment=dev --resource-group myResourceGroup"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/Leaves/delete", json={
                "help": {
                    "short": "Delete a monitor resource.",
                },
                "examples": [
                    {
                        "name": "Monitors Delete",
                        "commands": [
                            "elastic-monitor delete --name myMonitor --resource-group myResourceGroup"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/Leaves/list-deployment-info", json={
                "help": {
                    "short": "Fetch information regarding Elastic cloud deployment corresponding to the Elastic monitor resource.",
                },
                "examples": [
                    {
                        "name": "DeploymentInfo List",
                        "commands": [
                            "elastic-monitor list-deployment-info --name myMonitor --resource-group myResourceGroup"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/Leaves/list-resource", json={
                "help": {
                    "short": "List the resources currently being monitored by the Elastic monitor resource.",
                },
                "examples": [
                    {
                        "name": "MonitoredResources List",
                        "commands": [
                            "elastic-monitor list-resource --name myMonitor --resource-group myResourceGroup"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/Leaves/list-vm-host", json={
                "help": {
                    "short": "List the vm resources currently being monitored by the Elastic monitor resource.",
                },
                "examples": [
                    {
                        "name": "VMHost List",
                        "commands": [
                            "elastic-monitor list-vm-host --name myMonitor --resource-group myResourceGroup"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/Leaves/list-vm-ingestion-detail", json={
                "help": {
                    "short": "List the vm ingestion details that will be monitored by the Elastic monitor resource.",
                },
                "examples": [
                    {
                        "name": "VMIngestion Details",
                        "commands": [
                            "elastic-monitor list-vm-ingestion-detail --name myMonitor --resource-group myResourceGroup"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/Leaves/update-vm-collection", json={
                "help": {
                    "short": "Update the vm details that will be monitored by the Elastic monitor resource.",
                },
                "examples": [
                    {
                        "name": "VMCollection Update",
                        "commands": [
                            "elastic-monitor update-vm-collection --name myMonitor --resource-group myResourceGroup "
                            "--operation-name Add --vm-resource-id /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/myResourceGroup/providers/Microsoft.Compute/virtualmachines/myVM"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/tag-rule/Leaves/list", json={
                "help": {
                    "short": "List the tag rules for a given monitor resource.",
                },
                "examples": [
                    {
                        "name": "TagRules List",
                        "commands": [
                            "elastic-monitor tag-rule list --monitor-name myMonitor --resource-group myResourceGroup"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/tag-rule/Leaves/show", json={
                "help": {
                    "short": "Get a tag rule set for a given monitor resource.",
                },
                "examples": [
                    {
                        "name": "TagRules Get",
                        "commands": [
                            "elastic-monitor tag-rule show --monitor-name myMonitor --resource-group myResourceGroup --rule-set-name default"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/tag-rule/Leaves/create", json={
                "help": {
                    "short": "Create a tag rule set for a given monitor resource.",
                },
                "examples": [
                    {
                        "name": "TagRules Create",
                        "commands": [
                            "elastic-monitor tag-rule create --monitor-name myMonitor --resource-group myResourceGroup "
                            "--rule-set-name default --filtering-tags name=Environment action=Include value=Prod "
                            "--send-aad-logs False --send-activity-logs --send-subscription-logs "
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/tag-rule/Leaves/update", json={
                "help": {
                    "short": "Update a tag rule set for a given monitor resource.",
                },
                "examples": [
                    {
                        "name": "TagRules Update",
                        "commands": [
                            "elastic-monitor tag-rule update --monitor-name myMonitor --resource-group myResourceGroup "
                            "--rule-set-name default --send-aad-logs True"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/tag-rule/Leaves/delete", json={
                "help": {
                    "short": "Delete a tag rule set for a given monitor resource.",
                },
                "examples": [
                    {
                        "name": "TagRules Delete",
                        "commands": [
                            "elastic-monitor tag-rule delete --monitor-name myMonitor --resource-group myResourceGroup "
                            "--rule-set-name default"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.post(f"{ws_url}/Generate")
            self.assertTrue(rv.status_code == 200)

    @workspace_name("prepare_elastic_aaz_2021_09_01_preview")
    def prepare_elastic_aaz_2021_09_01_preview(self, ws_name):
        api_version = '2021-09-01-preview'
        module = 'elastic'
        with self.app.test_client() as c:
            rv = c.post(f"/AAZ/Editor/Workspaces", json={
                "name": ws_name,
                "plane": PlaneEnum.Mgmt,
            })
            self.assertTrue(rv.status_code == 200)
            ws = rv.get_json()
            ws_url = ws['url']
            rv = c.post(f"{ws_url}/CommandTree/Nodes/aaz/AddSwagger", json={
                'module': module,
                'version': api_version,
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
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Elastic/monitors/{monitorName}/createOrUpdateExternalUser')},
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

            rv = c.post(f"{ws_url}/CommandTree/Nodes/aaz/elastic/monitor/Rename", json={
                'name': "elastic-monitor"
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.delete(f"{ws_url}/CommandTree/Nodes/aaz/elastic", json={
                'name': "elastic-monitor"
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.post(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/Leaves/list-monitored-resource/Rename", json={
                'name': "elastic-monitor list-resource"
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.post(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/Leaves/vm-collection-update/Rename", json={
                'name': "elastic-monitor update-vm-collection"
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.post(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/Leaves/vm-ingestion-detail/Rename", json={
                'name': "elastic-monitor list-vm-ingestion-detail"
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.post(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/Leaves/create-or-update-external-user/Rename", json={
                'name': "elastic-monitor set-external-user"
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.get(f"{ws_url}/CommandTree/Nodes/aaz")
            self.assertTrue(rv.status_code == 200)
            command_tree = rv.get_json()

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor", json={
                "help": {
                    "short": "Manage monitor with Elastic.",
                },
                "stage": AAZStageEnum.Experimental
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/tag-rule", json={
                "help": {
                    "short": "Manage tag rule with Elastic.",
                },
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/Leaves/list", json={
                "help": {
                    "short": "List all monitors under the specified resource group. "
                             "And List all monitors under the specified subscription.",
                },
                "examples": [
                    {
                        "name": "Monitors List By ResourceGroup",
                        "commands": [
                            "elastic-monitor list --resource-group myResourceGroup"
                        ]
                    },
                    {
                        "name": "Monitors List",
                        "commands": [
                            "elastic-monitor list"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/Leaves/show", json={
                "help": {
                    "short": "Get the properties of a specific monitor resource.",
                },
                "examples": [
                    {
                        "name": "Monitors Get",
                        "commands": [
                            "elastic-monitor show --name myMonitor --resource-group myResourceGroup"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/Leaves/create", json={
                "help": {
                    "short": "Create a monitor resource.",
                },
                "examples": [
                    {
                        "name": "Monitors Create",
                        "commands": [
                            "elastic-monitor create --name myMonitor --location westus2"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/Leaves/update", json={
                "help": {
                    "short": "Update a monitor resource.",
                },
                "examples": [
                    {
                        "name": "Monitors Update",
                        "commands": [
                            "elastic-monitor update --name myMonitor --tags Environment=dev --resource-group myResourceGroup"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/Leaves/delete", json={
                "help": {
                    "short": "Delete a monitor resource.",
                },
                "examples": [
                    {
                        "name": "Monitors Delete",
                        "commands": [
                            "elastic-monitor delete --name myMonitor --resource-group myResourceGroup"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/Leaves/list-deployment-info", json={
                "help": {
                    "short": "Fetch information regarding Elastic cloud deployment corresponding to the Elastic monitor resource.",
                },
                "examples": [
                    {
                        "name": "DeploymentInfo List",
                        "commands": [
                            "elastic-monitor list-deployment-info --name myMonitor --resource-group myResourceGroup"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/Leaves/list-resource", json={
                "help": {
                    "short": "List the resources currently being monitored by the Elastic monitor resource.",
                },
                "examples": [
                    {
                        "name": "MonitoredResources List",
                        "commands": [
                            "elastic-monitor list-resource --name myMonitor --resource-group myResourceGroup"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/Leaves/list-vm-host", json={
                "help": {
                    "short": "List the vm resources currently being monitored by the Elastic monitor resource.",
                },
                "examples": [
                    {
                        "name": "VMHost List",
                        "commands": [
                            "elastic-monitor list-vm-host --name myMonitor --resource-group myResourceGroup"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/Leaves/list-vm-ingestion-detail", json={
                "help": {
                    "short": "List the vm ingestion details that will be monitored by the Elastic monitor resource.",
                },
                "examples": [
                    {
                        "name": "VMIngestion Details",
                        "commands": [
                            "elastic-monitor list-vm-ingestion-detail --name myMonitor --resource-group myResourceGroup"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/Leaves/update-vm-collection", json={
                "help": {
                    "short": "Update the vm details that will be monitored by the Elastic monitor resource.",
                },
                "examples": [
                    {
                        "name": "VMCollection Update",
                        "commands": [
                            "elastic-monitor update-vm-collection --name myMonitor --resource-group myResourceGroup "
                            "--operation-name Add --vm-resource-id /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/myResourceGroup/providers/Microsoft.Compute/virtualmachines/myVM"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/Leaves/set-external-user", json={
                "help": {
                    "short": "Manage User inside elastic deployment which are used by customers to perform operations on the elastic deployment.",
                },
                "examples": [
                    {
                        "name": "ExternalUserInfo",
                        "commands": [
                            "elastic-monitor set-external-user --name myMonitor --resource-group myResourceGroup "
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/tag-rule/Leaves/list", json={
                "help": {
                    "short": "List the tag rules for a given monitor resource.",
                },
                "examples": [
                    {
                        "name": "TagRules List",
                        "commands": [
                            "elastic-monitor tag-rule list --monitor-name myMonitor --resource-group myResourceGroup"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/tag-rule/Leaves/show", json={
                "help": {
                    "short": "Get a tag rule set for a given monitor resource.",
                },
                "examples": [
                    {
                        "name": "TagRules Get",
                        "commands": [
                            "elastic-monitor tag-rule show --monitor-name myMonitor --resource-group myResourceGroup --rule-set-name default"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/tag-rule/Leaves/create", json={
                "help": {
                    "short": "Create a tag rule set for a given monitor resource.",
                },
                "examples": [
                    {
                        "name": "TagRules Create",
                        "commands": [
                            "elastic-monitor tag-rule create --monitor-name myMonitor --resource-group myResourceGroup "
                            "--rule-set-name default --filtering-tags name=Environment action=Include value=Prod "
                            "--send-aad-logs False --send-activity-logs --send-subscription-logs "
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/tag-rule/Leaves/update", json={
                "help": {
                    "short": "Update a tag rule set for a given monitor resource.",
                },
                "examples": [
                    {
                        "name": "TagRules Update",
                        "commands": [
                            "elastic-monitor tag-rule update --monitor-name myMonitor --resource-group myResourceGroup "
                            "--rule-set-name default --send-aad-logs True"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/tag-rule/Leaves/delete", json={
                "help": {
                    "short": "Delete a tag rule set for a given monitor resource.",
                },
                "examples": [
                    {
                        "name": "TagRules Delete",
                        "commands": [
                            "elastic-monitor tag-rule delete --monitor-name myMonitor --resource-group myResourceGroup "
                            "--rule-set-name default"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.post(f"{ws_url}/Generate")
            self.assertTrue(rv.status_code == 200)

    @workspace_name("prepare_elastic_aaz_2021_10_01_preview")
    def prepare_elastic_aaz_2021_10_01_preview(self, ws_name):
        api_version = '2021-10-01-preview'
        module = 'elastic'
        with self.app.test_client() as c:
            rv = c.post(f"/AAZ/Editor/Workspaces", json={
                "name": ws_name,
                "plane": PlaneEnum.Mgmt,
            })
            self.assertTrue(rv.status_code == 200)
            ws = rv.get_json()
            ws_url = ws['url']
            rv = c.post(f"{ws_url}/CommandTree/Nodes/aaz/AddSwagger", json={
                'module': module,
                'version': api_version,
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
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Elastic/monitors/{monitorName}/createOrUpdateExternalUser')},
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
                    {'id': swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Elastic/monitors/{monitorName}/listUpgradableVersions')},
                    {'id': swagger_resource_path_to_resource_id(
                        '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Elastic/monitors/{monitorName}/upgrade')},
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.post(f"{ws_url}/CommandTree/Nodes/aaz/elastic/monitor/Rename", json={
                'name': "elastic-monitor"
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.delete(f"{ws_url}/CommandTree/Nodes/aaz/elastic", json={
                'name': "elastic-monitor"
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.post(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/Leaves/list-monitored-resource/Rename", json={
                'name': "elastic-monitor list-resource"
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.post(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/Leaves/vm-collection-update/Rename", json={
                'name': "elastic-monitor update-vm-collection"
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.post(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/Leaves/vm-ingestion-detail/Rename", json={
                'name': "elastic-monitor list-vm-ingestion-detail"
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.post(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/Leaves/create-or-update-external-user/Rename", json={
                'name': "elastic-monitor set-external-user"
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.post(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/Leaves/list-upgradable-version/Rename", json={
                'name': "elastic-monitor version list"
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.post(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/Leaves/upgrade/Rename", json={
                'name': "elastic-monitor version upgrade"
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.get(f"{ws_url}/CommandTree/Nodes/aaz")
            self.assertTrue(rv.status_code == 200)
            command_tree = rv.get_json()

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor", json={
                "help": {
                    "short": "Manage monitor with Elastic.",
                },
                "stage": AAZStageEnum.Preview
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/version", json={
                "help": {
                    "short": "Manage upgradable version for a monitor resource.",
                },
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/version/Leaves/list", json={
                "help": {
                    "short": "List of upgradable versions for a given monitor resource.",
                },
                "examples": [{
                    "name": "UpgradableVersionsList",
                    "commands": [
                        "elastic-monitor version list --name myMonitor --resource-group myGroup"
                    ]
                }]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/version/Leaves/upgrade", json={
                "help": {
                    "short": "List of upgradable versions for a given monitor resource.",
                },
                "examples": [{
                    "name": "UpgradableVersionsList",
                    "commands": [
                        "elastic-monitor version upgrade --name myMonitor --resource-group myGroup"
                    ]
                }]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/tag-rule", json={
                "help": {
                    "short": "Manage tag rule with Elastic.",
                },
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/Leaves/list", json={
                "help": {
                    "short": "List all monitors under the specified resource group. "
                             "And List all monitors under the specified subscription.",
                },
                "examples": [
                    {
                        "name": "Monitors List By ResourceGroup",
                        "commands": [
                            "elastic-monitor list --resource-group myResourceGroup"
                        ]
                    },
                    {
                        "name": "Monitors List",
                        "commands": [
                            "elastic-monitor list"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/Leaves/show", json={
                "help": {
                    "short": "Get the properties of a specific monitor resource.",
                },
                "examples": [
                    {
                        "name": "Monitors Get",
                        "commands": [
                            "elastic-monitor show --name myMonitor --resource-group myResourceGroup"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/Leaves/create", json={
                "help": {
                    "short": "Create a monitor resource.",
                },
                "examples": [
                    {
                        "name": "Monitors Create",
                        "commands": [
                            "elastic-monitor create --name myMonitor --location westus2"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/Leaves/update", json={
                "help": {
                    "short": "Update a monitor resource.",
                },
                "examples": [
                    {
                        "name": "Monitors Update",
                        "commands": [
                            "elastic-monitor update --name myMonitor --tags Environment=dev --resource-group myResourceGroup"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/Leaves/delete", json={
                "help": {
                    "short": "Delete a monitor resource.",
                },
                "examples": [
                    {
                        "name": "Monitors Delete",
                        "commands": [
                            "elastic-monitor delete --name myMonitor --resource-group myResourceGroup"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/Leaves/list-deployment-info", json={
                "help": {
                    "short": "Fetch information regarding Elastic cloud deployment corresponding to the Elastic monitor resource.",
                },
                "examples": [
                    {
                        "name": "DeploymentInfo List",
                        "commands": [
                            "elastic-monitor list-deployment-info --name myMonitor --resource-group myResourceGroup"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/Leaves/list-resource", json={
                "help": {
                    "short": "List the resources currently being monitored by the Elastic monitor resource.",
                },
                "examples": [
                    {
                        "name": "MonitoredResources List",
                        "commands": [
                            "elastic-monitor list-resource --name myMonitor --resource-group myResourceGroup"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/Leaves/list-vm-host", json={
                "help": {
                    "short": "List the vm resources currently being monitored by the Elastic monitor resource.",
                },
                "examples": [
                    {
                        "name": "VMHost List",
                        "commands": [
                            "elastic-monitor list-vm-host --name myMonitor --resource-group myResourceGroup"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/Leaves/list-vm-ingestion-detail", json={
                "help": {
                    "short": "List the vm ingestion details that will be monitored by the Elastic monitor resource.",
                },
                "examples": [
                    {
                        "name": "VMIngestion Details",
                        "commands": [
                            "elastic-monitor list-vm-ingestion-detail --name myMonitor --resource-group myResourceGroup"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/Leaves/update-vm-collection", json={
                "help": {
                    "short": "Update the vm details that will be monitored by the Elastic monitor resource.",
                },
                "examples": [
                    {
                        "name": "VMCollection Update",
                        "commands": [
                            "elastic-monitor update-vm-collection --name myMonitor --resource-group myResourceGroup "
                            "--operation-name Add --vm-resource-id /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/myResourceGroup/providers/Microsoft.Compute/virtualmachines/myVM"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/Leaves/set-external-user", json={
                "help": {
                    "short": "Manage User inside elastic deployment which are used by customers to perform operations on the elastic deployment.",
                },
                "examples": [
                    {
                        "name": "ExternalUserInfo",
                        "commands": [
                            "elastic-monitor set-external-user --name myMonitor --resource-group myResourceGroup "
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/tag-rule/Leaves/list", json={
                "help": {
                    "short": "List the tag rules for a given monitor resource.",
                },
                "examples": [
                    {
                        "name": "TagRules List",
                        "commands": [
                            "elastic-monitor tag-rule list --monitor-name myMonitor --resource-group myResourceGroup"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/tag-rule/Leaves/show", json={
                "help": {
                    "short": "Get a tag rule set for a given monitor resource.",
                },
                "examples": [
                    {
                        "name": "TagRules Get",
                        "commands": [
                            "elastic-monitor tag-rule show --monitor-name myMonitor --resource-group myResourceGroup --rule-set-name default"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/tag-rule/Leaves/create", json={
                "help": {
                    "short": "Create a tag rule set for a given monitor resource.",
                },
                "examples": [
                    {
                        "name": "TagRules Create",
                        "commands": [
                            "elastic-monitor tag-rule create --monitor-name myMonitor --resource-group myResourceGroup "
                            "--rule-set-name default --filtering-tags name=Environment action=Include value=Prod "
                            "--send-aad-logs False --send-activity-logs --send-subscription-logs "
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/tag-rule/Leaves/update", json={
                "help": {
                    "short": "Update a tag rule set for a given monitor resource.",
                },
                "examples": [
                    {
                        "name": "TagRules Update",
                        "commands": [
                            "elastic-monitor tag-rule update --monitor-name myMonitor --resource-group myResourceGroup "
                            "--rule-set-name default --send-aad-logs True"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.patch(f"{ws_url}/CommandTree/Nodes/aaz/elastic-monitor/tag-rule/Leaves/delete", json={
                "help": {
                    "short": "Delete a tag rule set for a given monitor resource.",
                },
                "examples": [
                    {
                        "name": "TagRules Delete",
                        "commands": [
                            "elastic-monitor tag-rule delete --monitor-name myMonitor --resource-group myResourceGroup "
                            "--rule-set-name default"
                        ]
                    }
                ]
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.post(f"{ws_url}/Generate")
            self.assertTrue(rv.status_code == 200)
