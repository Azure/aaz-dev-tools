from cli.tests.common import CommandTestCase
from utils.config import Config


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

    def _prepare_databricks(self):
        pass
