from ps.tests.common import CommandTestCase
from utils.config import Config


class APIPowerShellTest(CommandTestCase):

    def test_generate_sketch_profile(self):
        mod_name = "monitor"
        with self.app.test_client() as c:
            rv = c.get(f"/CLI/Az/Main/Modules/{mod_name}")
            self.assertTrue(rv.status_code == 200)
            data = rv.get_json()

            latest_profile = data["profiles"]["latest"]

            rv = c.post("/PS/Editor/GenerateSketcheProfile", json={"cliProfile": latest_profile})
            self.assertTrue(rv.status_code == 200)
            data = rv.get_json()
            self.assertTrue(len(data["resourceProviders"]) > 1)
