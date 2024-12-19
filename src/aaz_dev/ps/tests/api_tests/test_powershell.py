from ps.tests.common import CommandTestCase
from utils.config import Config
from utils.base64 import b64encode_str
from utils.stage import AAZStageEnum
# from cli.controller.az_module_manager import AzMainManager, AzExtensionManager
import os
import shutil
import yaml


class APIPowerShellTest(CommandTestCase):

    def test_get_powershell_path(self):
        with self.app.test_client() as c:
            print(Config.POWERSHELL_PATH)
            rv = c.get("/PS/Powershell/Path")
            self.assertTrue(rv.status_code == 200)
            data = rv.get_json()
            self.assertTrue(data["path"] == Config.POWERSHELL_PATH)

    def test_list_powershell_modules(self):
        config_dict = {}
        with self.app.test_client() as c:
            rv = c.get("/PS/Powershell/Modules")
            self.assertTrue(rv.status_code == 200)
            data = rv.get_json()
            self.assertTrue(len(data) > 100)
            self.assertTrue(all(module["name"].endswith(".Autorest") for module in data))
            for module in data:
                request_url = module["url"]
                rv = c.get(request_url)
                self.assertTrue(rv.status_code == 200)
                data = rv.get_json()
                if data["autorest_config"] is None:
                    continue
                for key, value in data["autorest_config"].items():
                    if key in ["directive", "commit", "input-file", "title", "module-version"]:
                        continue
                    if key not in config_dict:
                        config_dict[key] = {
                            "list": set(),
                            "dict": {},
                            "basic": set(),
                        }
                    if isinstance(value, list):
                        config_dict[key]["list"].update(value)
                    elif isinstance(value, dict):
                        config_dict[key]["dict"].update(value)
                    else:
                        config_dict[key]["basic"].add(value)
        for key, value in config_dict.items():
            if not len(value["list"]):
                del value["list"]
            else:
                value["list"] = sorted(list(value["list"]))
            if not len(value["dict"]):
                del value["dict"]
            if not len(value["basic"]):
                del value["basic"]
            else:
                value["basic"] = sorted(list(value["basic"]))
        # with open("ps/templates/autorest/config_common_used_props.yaml", "w") as f:
        #     yaml.dump(config_dict, f)
