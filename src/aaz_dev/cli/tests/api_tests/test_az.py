from cli.tests.common import CommandTestCase
from utils.config import Config
from utils.base64 import b64encode_str
from utils.stage import AAZStageEnum
from cli.controller.az_module_manager import AzMainManager, AzExtensionManager
import os
import shutil


class APIAzTest(CommandTestCase):

    def test_list_profiles(self):
        with self.app.test_client() as c:
            rv = c.get(f"/CLI/Az/Profiles")
            self.assertTrue(rv.status_code == 200)
            data = rv.get_json()
            self.assertTrue(data == Config.CLI_PROFILES)

    def test_list_main_modules(self):
        with self.app.test_client() as c:
            rv = c.get(f"/CLI/Az/Main/Modules")
            self.assertTrue(rv.status_code == 200)
            data = rv.get_json()
            self.assertTrue(len(data))
            self.assertTrue('name' in data[0])
            self.assertTrue('folder' in data[0])
            self.assertTrue('url' in data[0])
            for mod in data:
                rv = c.get(mod['url'])
                self.assertTrue(rv.status_code == 200)

    def test_list_extension_modules(self):
        with self.app.test_client() as c:
            rv = c.get(f"/CLI/Az/Extension/Modules")
            self.assertTrue(rv.status_code == 200)
            data = rv.get_json()
            self.assertTrue(len(data))
            self.assertTrue('name' in data[0])
            self.assertTrue('folder' in data[0])
            self.assertTrue('url' in data[0])
            for mod in data:
                rv = c.get(mod['url'])
                self.assertTrue(rv.status_code == 200, mod['url'])

    def test_transfer_command_group(self):
        self.prepare_aaz()
        with self.app.test_client() as c:
            rv = c.post(f"/CLI/Az/AAZ/Specs/CommandTree/Nodes/aaz/data-bricks/Transfer")
            self.assertTrue(rv.status_code == 200)
            data = rv.get_json()
            self.assertTrue(data['names'] == ['data-bricks'])
            self.assertTrue(data['help']['short'] == 'Manage databricks workspaces.')

            rv = c.post(f"/CLI/Az/AAZ/Specs/CommandTree/Nodes/aaz/data-bricks/workspace/Transfer")
            self.assertTrue(rv.status_code == 200)
            data = rv.get_json()
            self.assertTrue(data['names'] == ['data-bricks', 'workspace'])
            self.assertTrue(data['help']['short'] == 'Commands to manage databricks workspace.')

            rv = c.post(f"/CLI/Az/AAZ/Specs/CommandTree/Nodes/aaz/data-bricks/workspace/vnet-peering/Transfer")
            self.assertTrue(rv.status_code == 200)
            data = rv.get_json()
            self.assertTrue(data['names'] == ['data-bricks', 'workspace', 'vnet-peering'])
            self.assertTrue(data['help']['short'] == 'Commands to manage databricks workspace vnet peering.')

    def test_transfer_command(self):
        self.prepare_aaz()

        with self.app.test_client() as c:
            version = '2018-04-01'
            rv = c.post(f"/CLI/Az/AAZ/Specs/CommandTree/Nodes/aaz/data-bricks/workspace/Leaves/create/Versions/{b64encode_str(version)}/Transfer")
            self.assertTrue(rv.status_code == 200)
            data = rv.get_json()
            self.assertTrue(data['names'] == ['data-bricks', 'workspace', 'create'])
            self.assertTrue(data['version'] == '2018-04-01')
            self.assertTrue(data['help'] == {
                'short': 'Create a new workspace.',
                'examples': [
                    {
                        'commands': [
                            'data-bricks workspace create --resource-group MyResourceGroup --name MyWorkspace --location westus --sku standard'],
                        'name': 'Create a workspace'
                    },
                    {
                        'commands': [
                            'data-bricks workspace create --resource-group MyResourceGroup --name MyWorkspace --location eastus2euap --sku premium --prepare-encryption'],
                        'name': 'Create a workspace with managed identity for storage account'
                    }
                ],
            })
            self.assertTrue(data['resources'] == [
                {
                    'id': '/subscriptions/{}/resourcegroups/{}/providers/microsoft.databricks/workspaces/{}',
                    'plane': 'mgmt-plane',
                    'version': '2018-04-01'
                }
            ])

            version = '2021-04-01-preview'
            rv = c.post(
                f"/CLI/Az/AAZ/Specs/CommandTree/Nodes/aaz/data-bricks/workspace/Leaves/create/Versions/{b64encode_str(version)}/Transfer")
            self.assertTrue(rv.status_code == 200)
            data = rv.get_json()
            self.assertTrue(data['names'] == ['data-bricks', 'workspace', 'create'])
            self.assertTrue(data['version'] == '2021-04-01-preview')
            self.assertTrue(data['stage'] == AAZStageEnum.Preview)
            self.assertTrue(data['help'] == {
                'short': 'Create a new workspace.',
                'examples': [
                    {
                        'commands': [
                            'data-bricks workspace create --resource-group MyResourceGroup --name MyWorkspace --location westus --sku standard'],
                        'name': 'Create a workspace'
                    },
                    {
                        'commands': [
                            'data-bricks workspace create --resource-group MyResourceGroup --name MyWorkspace --location eastus2euap --sku premium --prepare-encryption'],
                        'name': 'Create a workspace with managed identity for storage account'
                    }
                ],
            })
            self.assertTrue(data['resources'] == [
                {
                    'id': '/subscriptions/{}/resourcegroups/{}/providers/microsoft.databricks/workspaces/{}',
                    'plane': 'mgmt-plane',
                    'version': '2021-04-01-preview'
                }
            ])

    def test_create_new_module_in_main(self):
        mod_name = "aaz-new-module"
        manager = AzMainManager()
        path = manager.get_mod_path(mod_name)
        if os.path.exists(path):
            shutil.rmtree(path, ignore_errors=True)
        try:
            with self.app.test_client() as c:
                rv = c.post(f"/CLI/Az/Main/Modules", json={
                    "name": mod_name
                })
                self.assertTrue(rv.status_code == 200)
                data = rv.get_json()
                self.assertTrue(data['name'] == mod_name)
                self.assertTrue(data['folder'] == path)
                for profile_name in Config.CLI_PROFILES:
                    self.assertTrue(profile_name in data['profiles'])
                    self.assertTrue(data['profiles'][profile_name] == {'name': profile_name})
        finally:
            shutil.rmtree(path, ignore_errors=True)

    def test_create_new_module_in_extension(self):
        mod_name = "aaz-new-extension"
        manager = AzExtensionManager()
        path = manager.get_mod_path(mod_name)
        if os.path.exists(path):
            shutil.rmtree(path, ignore_errors=True)
        try:
            with self.app.test_client() as c:
                rv = c.post(f"/CLI/Az/Extension/Modules", json={
                    "name": mod_name
                })
                self.assertTrue(rv.status_code == 200)
                data = rv.get_json()
                self.assertTrue(data['name'] == mod_name)
                self.assertTrue(data['folder'] == path)
                for profile_name in Config.CLI_PROFILES:
                    self.assertTrue(profile_name in data['profiles'])
                    self.assertTrue(data['profiles'][profile_name] == {'name': profile_name})
        finally:
            shutil.rmtree(path, ignore_errors=True)

    def test_generate_edge_order_in_main_repo(self):
        self.prepare_aaz()
        mod_name = "aaz-edge-order"
        manager = AzMainManager()
        path = manager.get_mod_path(mod_name)
        if os.path.exists(path):
            shutil.rmtree(path, ignore_errors=True)
        with self.app.test_client() as c:
            rv = c.post(f"/CLI/Az/Main/Modules", json={
                "name": mod_name
            })
            self.assertTrue(rv.status_code == 200)
            profiles = rv.get_json()['profiles']

            # latest profile
            version = '2021-12-01'
            profile = profiles[Config.CLI_DEFAULT_PROFILE]
            rv = c.post(f"/CLI/Az/AAZ/Specs/CommandTree/Nodes/aaz/edge-order/Transfer")
            self.assertTrue(rv.status_code == 200)
            data = rv.get_json()
            profile['commandGroups'] = {
                'edge-order': data
            }

            edge_order = profile['commandGroups']['edge-order']
            edge_order['commandGroups'] = {}

            rv = c.post(f"/CLI/Az/AAZ/Specs/CommandTree/Nodes/aaz/edge-order/address/Transfer")
            self.assertTrue(rv.status_code == 200)
            data = rv.get_json()
            edge_order['commandGroups']['address'] = data

            address = profile['commandGroups']['edge-order']['commandGroups']['address']
            address['commands'] = {}

            rv = c.post(f"/CLI/Az/AAZ/Specs/CommandTree/Nodes/aaz/edge-order/address/Leaves/create/Versions/{b64encode_str(version)}/Transfer")
            self.assertTrue(rv.status_code == 200)
            data = rv.get_json()
            address['commands']['create'] = data

            rv = c.post(
                f"/CLI/Az/AAZ/Specs/CommandTree/Nodes/aaz/edge-order/address/Leaves/delete/Versions/{b64encode_str(version)}/Transfer")
            self.assertTrue(rv.status_code == 200)
            data = rv.get_json()
            address['commands']['delete'] = data

            rv = c.post(
                f"/CLI/Az/AAZ/Specs/CommandTree/Nodes/aaz/edge-order/address/Leaves/list/Versions/{b64encode_str(version)}/Transfer")
            self.assertTrue(rv.status_code == 200)
            data = rv.get_json()
            address['commands']['list'] = data

            rv = c.post(
                f"/CLI/Az/AAZ/Specs/CommandTree/Nodes/aaz/edge-order/address/Leaves/show/Versions/{b64encode_str(version)}/Transfer")
            self.assertTrue(rv.status_code == 200)
            data = rv.get_json()
            address['commands']['show'] = data

            rv = c.post(
                f"/CLI/Az/AAZ/Specs/CommandTree/Nodes/aaz/edge-order/address/Leaves/update/Versions/{b64encode_str(version)}/Transfer")
            self.assertTrue(rv.status_code == 200)
            data = rv.get_json()
            address['commands']['update'] = data

            rv = c.post(f"/CLI/Az/AAZ/Specs/CommandTree/Nodes/aaz/edge-order/order/Transfer")
            self.assertTrue(rv.status_code == 200)
            data = rv.get_json()
            edge_order['commandGroups']['order'] = data

            order = profile['commandGroups']['edge-order']['commandGroups']['order']
            order['commands'] = {}

            rv = c.post(
                f"/CLI/Az/AAZ/Specs/CommandTree/Nodes/aaz/edge-order/order/Leaves/list/Versions/{b64encode_str(version)}/Transfer")
            self.assertTrue(rv.status_code == 200)
            data = rv.get_json()
            order['commands']['list'] = data

            rv = c.post(
                f"/CLI/Az/AAZ/Specs/CommandTree/Nodes/aaz/edge-order/order/Leaves/show/Versions/{b64encode_str(version)}/Transfer")
            self.assertTrue(rv.status_code == 200)
            data = rv.get_json()
            order['commands']['show'] = data

            rv = c.post(f"/CLI/Az/AAZ/Specs/CommandTree/Nodes/aaz/edge-order/order-item/Transfer")
            self.assertTrue(rv.status_code == 200)
            data = rv.get_json()
            edge_order['commandGroups']['order-item'] = data

            order_item = profile['commandGroups']['edge-order']['commandGroups']['order-item']
            order_item['commands'] = {}

            rv = c.post(
                f"/CLI/Az/AAZ/Specs/CommandTree/Nodes/aaz/edge-order/order-item/Leaves/cancel/Versions/{b64encode_str(version)}/Transfer")
            self.assertTrue(rv.status_code == 200)
            data = rv.get_json()
            order_item['commands']['cancel'] = data

            rv = c.post(
                f"/CLI/Az/AAZ/Specs/CommandTree/Nodes/aaz/edge-order/order-item/Leaves/create/Versions/{b64encode_str(version)}/Transfer")
            self.assertTrue(rv.status_code == 200)
            data = rv.get_json()
            order_item['commands']['create'] = data

            rv = c.post(
                f"/CLI/Az/AAZ/Specs/CommandTree/Nodes/aaz/edge-order/order-item/Leaves/delete/Versions/{b64encode_str(version)}/Transfer")
            self.assertTrue(rv.status_code == 200)
            data = rv.get_json()
            order_item['commands']['delete'] = data

            rv = c.post(
                f"/CLI/Az/AAZ/Specs/CommandTree/Nodes/aaz/edge-order/order-item/Leaves/list/Versions/{b64encode_str(version)}/Transfer")
            self.assertTrue(rv.status_code == 200)
            data = rv.get_json()
            order_item['commands']['list'] = data

            rv = c.post(
                f"/CLI/Az/AAZ/Specs/CommandTree/Nodes/aaz/edge-order/order-item/Leaves/return/Versions/{b64encode_str(version)}/Transfer")
            self.assertTrue(rv.status_code == 200)
            data = rv.get_json()
            order_item['commands']['return'] = data

            rv = c.post(
                f"/CLI/Az/AAZ/Specs/CommandTree/Nodes/aaz/edge-order/order-item/Leaves/show/Versions/{b64encode_str(version)}/Transfer")
            self.assertTrue(rv.status_code == 200)
            data = rv.get_json()
            order_item['commands']['show'] = data

            rv = c.post(
                f"/CLI/Az/AAZ/Specs/CommandTree/Nodes/aaz/edge-order/order-item/Leaves/update/Versions/{b64encode_str(version)}/Transfer")
            self.assertTrue(rv.status_code == 200)
            data = rv.get_json()
            order_item['commands']['update'] = data

            # 2020-09-01-hybrid profile
            version = '2020-12-01-preview'
            profile = profiles[Config.CLI_PROFILES[1]]

            rv = c.post(f"/CLI/Az/AAZ/Specs/CommandTree/Nodes/aaz/edge-order/Transfer")
            self.assertTrue(rv.status_code == 200)
            data = rv.get_json()
            profile['commandGroups'] = {
                'edge-order': data
            }

            edge_order = profile['commandGroups']['edge-order']
            edge_order['commandGroups'] = {}

            rv = c.post(f"/CLI/Az/AAZ/Specs/CommandTree/Nodes/aaz/edge-order/address/Transfer")
            self.assertTrue(rv.status_code == 200)
            data = rv.get_json()
            edge_order['commandGroups']['address'] = data

            address = profile['commandGroups']['edge-order']['commandGroups']['address']
            address['commands'] = {}

            rv = c.post(
                f"/CLI/Az/AAZ/Specs/CommandTree/Nodes/aaz/edge-order/address/Leaves/create/Versions/{b64encode_str(version)}/Transfer")
            self.assertTrue(rv.status_code == 200)
            data = rv.get_json()
            address['commands']['create'] = data

            rv = c.post(
                f"/CLI/Az/AAZ/Specs/CommandTree/Nodes/aaz/edge-order/address/Leaves/delete/Versions/{b64encode_str(version)}/Transfer")
            self.assertTrue(rv.status_code == 200)
            data = rv.get_json()
            address['commands']['delete'] = data

            rv = c.post(
                f"/CLI/Az/AAZ/Specs/CommandTree/Nodes/aaz/edge-order/address/Leaves/list/Versions/{b64encode_str(version)}/Transfer")
            self.assertTrue(rv.status_code == 200)
            data = rv.get_json()
            address['commands']['list'] = data

            rv = c.post(
                f"/CLI/Az/AAZ/Specs/CommandTree/Nodes/aaz/edge-order/address/Leaves/show/Versions/{b64encode_str(version)}/Transfer")
            self.assertTrue(rv.status_code == 200)
            data = rv.get_json()
            address['commands']['show'] = data

            rv = c.post(
                f"/CLI/Az/AAZ/Specs/CommandTree/Nodes/aaz/edge-order/address/Leaves/update/Versions/{b64encode_str(version)}/Transfer")
            self.assertTrue(rv.status_code == 200)
            data = rv.get_json()
            address['commands']['update'] = data

            rv = c.post(f"/CLI/Az/AAZ/Specs/CommandTree/Nodes/aaz/edge-order/order/Transfer")
            self.assertTrue(rv.status_code == 200)
            data = rv.get_json()
            edge_order['commandGroups']['order'] = data

            order = profile['commandGroups']['edge-order']['commandGroups']['order']
            order['commands'] = {}

            rv = c.post(
                f"/CLI/Az/AAZ/Specs/CommandTree/Nodes/aaz/edge-order/order/Leaves/list/Versions/{b64encode_str(version)}/Transfer")
            self.assertTrue(rv.status_code == 200)
            data = rv.get_json()
            order['commands']['list'] = data

            rv = c.post(
                f"/CLI/Az/AAZ/Specs/CommandTree/Nodes/aaz/edge-order/order/Leaves/show/Versions/{b64encode_str(version)}/Transfer")
            self.assertTrue(rv.status_code == 200)
            data = rv.get_json()
            order['commands']['show'] = data

            rv = c.post(f"/CLI/Az/AAZ/Specs/CommandTree/Nodes/aaz/edge-order/order-item/Transfer")
            self.assertTrue(rv.status_code == 200)
            data = rv.get_json()
            edge_order['commandGroups']['order-item'] = data

            order_item = profile['commandGroups']['edge-order']['commandGroups']['order-item']
            order_item['commands'] = {}

            rv = c.post(
                f"/CLI/Az/AAZ/Specs/CommandTree/Nodes/aaz/edge-order/order-item/Leaves/cancel/Versions/{b64encode_str(version)}/Transfer")
            self.assertTrue(rv.status_code == 200)
            data = rv.get_json()
            order_item['commands']['cancel'] = data

            rv = c.post(
                f"/CLI/Az/AAZ/Specs/CommandTree/Nodes/aaz/edge-order/order-item/Leaves/create/Versions/{b64encode_str(version)}/Transfer")
            self.assertTrue(rv.status_code == 200)
            data = rv.get_json()
            order_item['commands']['create'] = data

            rv = c.post(
                f"/CLI/Az/AAZ/Specs/CommandTree/Nodes/aaz/edge-order/order-item/Leaves/delete/Versions/{b64encode_str(version)}/Transfer")
            self.assertTrue(rv.status_code == 200)
            data = rv.get_json()
            order_item['commands']['delete'] = data

            rv = c.post(
                f"/CLI/Az/AAZ/Specs/CommandTree/Nodes/aaz/edge-order/order-item/Leaves/list/Versions/{b64encode_str(version)}/Transfer")
            self.assertTrue(rv.status_code == 200)
            data = rv.get_json()
            order_item['commands']['list'] = data

            rv = c.post(
                f"/CLI/Az/AAZ/Specs/CommandTree/Nodes/aaz/edge-order/order-item/Leaves/return/Versions/{b64encode_str(version)}/Transfer")
            self.assertTrue(rv.status_code == 200)
            data = rv.get_json()
            order_item['commands']['return'] = data

            rv = c.post(
                f"/CLI/Az/AAZ/Specs/CommandTree/Nodes/aaz/edge-order/order-item/Leaves/show/Versions/{b64encode_str(version)}/Transfer")
            self.assertTrue(rv.status_code == 200)
            data = rv.get_json()
            order_item['commands']['show'] = data

            rv = c.post(
                f"/CLI/Az/AAZ/Specs/CommandTree/Nodes/aaz/edge-order/order-item/Leaves/update/Versions/{b64encode_str(version)}/Transfer")
            self.assertTrue(rv.status_code == 200)
            data = rv.get_json()
            order_item['commands']['update'] = data

            rv = c.put(f"/CLI/Az/Main/Modules/{mod_name}", json={
                "profiles": profiles
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.get(f"/CLI/Az/Main/Modules/{mod_name}")
            self.assertTrue(rv.status_code == 200)
            data = rv.get_json()
            self.assertTrue(data['profiles'] == profiles)

    # databricks has object whose value type can be anything https://github.com/Azure/azure-rest-api-specs/blob/2c66a689c610dbef623d6c4e4c4e913446d5ac68/specification/databricks/resource-manager/Microsoft.Databricks/stable/2018-04-01/databricks.json#L594-L609
    # def test_generate_databricks_in_main_repo(self):
    #     self.prepare_aaz()
    #     mod_name = "aaz-data-bricks"
    #     manager = AzMainManager()
    #     path = manager.get_mod_path(mod_name)
    #     if os.path.exists(path):
    #         shutil.rmtree(path, ignore_errors=True)
    #     with self.app.test_client() as c:
    #         rv = c.post(f"/CLI/Az/Main/Modules", json={
    #             "name": mod_name
    #         })
    #         self.assertTrue(rv.status_code == 200)
    #         profiles = rv.get_json()['profiles']
    #
    #         # latest profile
    #         version = '2018-04-01'
    #         profile = profiles[Config.CLI_DEFAULT_PROFILE]
    #         rv = c.post(f"/CLI/Az/AAZ/Specs/CommandTree/Nodes/aaz/data-bricks/Transfer")
    #         self.assertTrue(rv.status_code == 200)
    #         data = rv.get_json()
    #         profile['commandGroups'] = {
    #             'data-bricks': data
    #         }
    #
    #         rv = c.post(f"/CLI/Az/AAZ/Specs/CommandTree/Nodes/aaz/data-bricks/workspace/Transfer")
    #         self.assertTrue(rv.status_code == 200)
    #         data = rv.get_json()
    #         profile['commandGroups']['data-bricks']['commandGroups'] = {
    #             'workspace': data,
    #         }
    #
    #         workspace = profile['commandGroups']['data-bricks']['commandGroups']['workspace']
    #         rv = c.post(f"/CLI/Az/AAZ/Specs/CommandTree/Nodes/aaz/data-bricks/workspace/vnet-peering/Transfer")
    #         self.assertTrue(rv.status_code == 200)
    #         data = rv.get_json()
    #         workspace['commandGroups'] = {
    #             'vnet-peering': data
    #         }
    #
    #         workspace['commands'] = {}
    #
    #         rv = c.post(f"/CLI/Az/AAZ/Specs/CommandTree/Nodes/aaz/data-bricks/workspace/Leaves/create/Versions/{b64encode_str(version)}/Transfer")
    #         self.assertTrue(rv.status_code == 200)
    #         data = rv.get_json()
    #         workspace['commands']['create'] = data
    #
    #         rv = c.post(f"/CLI/Az/AAZ/Specs/CommandTree/Nodes/aaz/data-bricks/workspace/Leaves/delete/Versions/{b64encode_str(version)}/Transfer")
    #         self.assertTrue(rv.status_code == 200)
    #         data = rv.get_json()
    #         workspace['commands']['delete'] = data
    #
    #         rv = c.post(f"/CLI/Az/AAZ/Specs/CommandTree/Nodes/aaz/data-bricks/workspace/Leaves/list/Versions/{b64encode_str(version)}/Transfer")
    #         self.assertTrue(rv.status_code == 200)
    #         data = rv.get_json()
    #         workspace['commands']['list'] = data
    #
    #         rv = c.post(f"/CLI/Az/AAZ/Specs/CommandTree/Nodes/aaz/data-bricks/workspace/Leaves/show/Versions/{b64encode_str(version)}/Transfer")
    #         self.assertTrue(rv.status_code == 200)
    #         data = rv.get_json()
    #         workspace['commands']['show'] = data
    #
    #         rv = c.post(f"/CLI/Az/AAZ/Specs/CommandTree/Nodes/aaz/data-bricks/workspace/Leaves/update/Versions/{b64encode_str(version)}/Transfer")
    #         self.assertTrue(rv.status_code == 200)
    #         data = rv.get_json()
    #         workspace['commands']['update'] = data
    #
    #         vnet_peering = profile['commandGroups']['data-bricks']['commandGroups']['workspace']['commandGroups']['vnet-peering']
    #         vnet_peering['commands'] = {}
    #
    #         rv = c.post(
    #             f"/CLI/Az/AAZ/Specs/CommandTree/Nodes/aaz/data-bricks/workspace/vnet-peering/Leaves/create/Versions/{b64encode_str(version)}/Transfer")
    #         self.assertTrue(rv.status_code == 200)
    #         data = rv.get_json()
    #         vnet_peering['commands']['create'] = data
    #
    #         rv = c.post(
    #             f"/CLI/Az/AAZ/Specs/CommandTree/Nodes/aaz/data-bricks/workspace/vnet-peering/Leaves/delete/Versions/{b64encode_str(version)}/Transfer")
    #         self.assertTrue(rv.status_code == 200)
    #         data = rv.get_json()
    #         vnet_peering['commands']['delete'] = data
    #
    #         rv = c.post(
    #             f"/CLI/Az/AAZ/Specs/CommandTree/Nodes/aaz/data-bricks/workspace/vnet-peering/Leaves/list/Versions/{b64encode_str(version)}/Transfer")
    #         self.assertTrue(rv.status_code == 200)
    #         data = rv.get_json()
    #         vnet_peering['commands']['list'] = data
    #
    #         rv = c.post(
    #             f"/CLI/Az/AAZ/Specs/CommandTree/Nodes/aaz/data-bricks/workspace/vnet-peering/Leaves/show/Versions/{b64encode_str(version)}/Transfer")
    #         self.assertTrue(rv.status_code == 200)
    #         data = rv.get_json()
    #         vnet_peering['commands']['show'] = data
    #
    #         rv = c.post(
    #             f"/CLI/Az/AAZ/Specs/CommandTree/Nodes/aaz/data-bricks/workspace/vnet-peering/Leaves/update/Versions/{b64encode_str(version)}/Transfer")
    #         self.assertTrue(rv.status_code == 200)
    #         data = rv.get_json()
    #         vnet_peering['commands']['update'] = data
    #
    #         rv = c.put(f"/CLI/Az/Main/Modules/{mod_name}", json={
    #             "profiles": profiles
    #         })
    #         self.assertTrue(rv.status_code == 200)
    #
    #         # hybrid_profile = profiles["2020-09-01-hybrid"]
    #         # hybrid_profile['commandGroups'] = {
    #         #     "data-bricks": data
    #         # }


