from unittest import TestCase
from app.app import create_app
from utils.config import Config
import shutil
import os


class ApiTestCase(TestCase):
    AAZ_DEV_FOLDER = os.path.expanduser(os.path.join('~', '.aaz_dev_test'))
    AAZ_FOLDER = os.path.expanduser(os.path.join('~', '.aaz_test'))

    def __init__(self, *args, **kwargs):
        self.cleanup_dev_folder()
        Config.AAZ_PATH = self.AAZ_FOLDER
        Config.AAZ_DEV_FOLDER = self.AAZ_DEV_FOLDER
        Config.AAZ_DEV_WORKSPACE_FOLDER = os.path.join(self.AAZ_DEV_FOLDER, 'workspaces')
        super().__init__(*args, **kwargs)
        self.app = create_app()
        self.app.testing = True
        self.addCleanup(self.cleanup_dev_folder)

    def cleanup_dev_folder(self):
        if os.path.exists(self.AAZ_DEV_FOLDER):
            shutil.rmtree(self.AAZ_DEV_FOLDER)
        if os.path.exists(self.AAZ_FOLDER):
            shutil.rmtree(self.AAZ_FOLDER)

    def setUp(self):
        os.makedirs(self.AAZ_FOLDER, exist_ok=True)
        # the fake aaz repo is wiped for every test, seed it with an empty command tree so that
        # loading the command tree doesn't fail on a missing readme.md
        commands_folder = os.path.join(self.AAZ_FOLDER, 'Commands')
        os.makedirs(commands_folder, exist_ok=True)
        with open(os.path.join(commands_folder, 'readme.md'), 'w', encoding='utf-8') as f:
            f.write("# Atomic Azure CLI Commands\n\n## Groups\n\n")

