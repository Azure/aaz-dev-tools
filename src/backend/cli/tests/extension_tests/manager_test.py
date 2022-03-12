import os
import shutil

from cli.tests.common import CommandTestCase
from cli.controller.az_module_manager import AzExtensionManager


class CliExtensionManagerTest(CommandTestCase):

    def test_create_new_extension(self):
        mod_name = "new-extension"
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", mod_name)
        if os.path.exists:
            shutil.rmtree(path, ignore_errors=True)
        manager = AzExtensionManager()
        manager.get_mod_path = lambda _: path
        manager.create_new_mod(mod_name)

    def test_patch_aaz_extension(self):
        mod_name = "application-insights"
        manager = AzExtensionManager()
        mod_path = manager.get_mod_path(mod_name)
        mod_path = os.path.abspath(mod_path)
        output_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", mod_name)
        for file_path, file_data in manager._patch_module(mod_name):
            file_path = os.path.abspath(file_path).replace(mod_path, output_folder)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w') as f:
                f.write(file_data)
