import os
import shutil

from cli.tests.common import CommandTestCase
from cli.controller.az_module_manager import AzMainManager


class CliMainManagerTest(CommandTestCase):

    def test_create_new_module(self):
        mod_name = "new-module"
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", mod_name)
        if os.path.exists(path):
            shutil.rmtree(path, ignore_errors=True)
        manager = AzMainManager()
        manager.get_mod_path = lambda _: path
        manager.create_new_mod(mod_name)

    def test_patch_module(self):
        mod_name = "monitor"
        manager = AzMainManager()
        mod_path = manager.get_mod_path(mod_name)
        mod_path = os.path.abspath(mod_path)
        output_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", mod_name)
        for file_path, file_data in manager._patch_module(mod_name):
            file_path = os.path.abspath(file_path).replace(mod_path, output_folder)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w') as f:
                f.write(file_data)

    def test_patch_module_with_special_args(self):
        mod_name = "interactive"
        manager = AzMainManager()
        mod_path = manager.get_mod_path(mod_name)
        mod_path = os.path.abspath(mod_path)
        output_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", mod_name)
        for file_path, file_data in manager._patch_module(mod_name):
            file_path = os.path.abspath(file_path).replace(mod_path, output_folder)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w') as f:
                f.write(file_data)

