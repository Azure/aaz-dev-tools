from cli.tests.common import CommandTestCase
from utils.config import Config
from utils.base64 import b64encode_str
from utils.stage import AAZStageEnum


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
