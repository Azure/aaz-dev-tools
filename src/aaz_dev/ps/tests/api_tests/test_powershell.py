from ps.tests.common import CommandTestCase
from utils.config import Config


class APIPowerShellTest(CommandTestCase):

    def test_get_powershell_path(self):
        with self.app.test_client() as c:
            print(Config.POWERSHELL_PATH)
            rv = c.get("/PS/Powershell/Path")
            self.assertTrue(rv.status_code == 200)
            data = rv.get_json()
            self.assertTrue(data["path"] == Config.POWERSHELL_PATH)

    def test_list_powershell_modules(self):
        with self.app.test_client() as c:
            rv = c.get("/PS/Powershell/Modules")
            self.assertTrue(rv.status_code == 200)
            data = rv.get_json()
            self.assertTrue(len(data) > 100)
            self.assertTrue(all(module["name"].endswith(".Autorest") for module in data))
            for module in data:
                if module["name"] in [
                    "Communication/EmailServicedata.Autorest",
                    "ManagedServiceIdentity/ManagedServiceIdentity.Autorest", "VoiceServices/VoiceServices.Autorest",
                    "Resources/MSGraph.Autorest", "Migrate/Migrate.Autorest"
                ]:
                    continue
                request_url = module["url"]
                rv = c.get(request_url)
                self.assertTrue(rv.status_code == 200)
                data = rv.get_json()
