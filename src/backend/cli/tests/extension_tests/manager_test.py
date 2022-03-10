import os
import shutil

from cli.tests.common import CommandTestCase
from cli.controller.az_module_manager import AzExtensionManager


class CliExtensionManagerTest(CommandTestCase):

    def test_create_new_extension(self):
        mod_name = "aaz-new-extension"
        manager = AzExtensionManager()
        mod_path = manager.get_mod_path(mod_name)
        if os.path.exists(mod_path):
            shutil.rmtree(mod_path)
        try:
            manager.create_new_mod(mod_name)
        finally:
            if os.path.exists(mod_path):
                shutil.rmtree(mod_path)
