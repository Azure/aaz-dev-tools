import os
import shutil

from cli.tests.common import CommandTestCase
from cli.controller.az_main_manager import AzMainManager


class CliMainManagerTest(CommandTestCase):

    def test_create_new_module(self):
        mod_name = "aaz-new-module"
        manager = AzMainManager()
        mod_path = manager.get_mod_path(mod_name)
        if os.path.exists(mod_path):
            shutil.rmtree(mod_path)
        try:
            manager.create_new_mod(mod_name)
        finally:
            if os.path.exists(mod_path):
                shutil.rmtree(mod_path)
