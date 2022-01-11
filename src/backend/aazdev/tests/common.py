from unittest import TestCase
from aazdev.app import create_app
from utils.config import Config
import os
import shutil


class ApiTestCase(TestCase):
    AAZ_DEV_FOLDER = os.path.expanduser(os.path.join('~', '.aaz_dev_test'))

    def __init__(self, *args, **kwargs):
        self.cleanup_dev_folder()
        Config.AAZ_DEV_FOLDER = self.AAZ_DEV_FOLDER
        Config.AAZ_DEV_WORKSPACE_FOLDER = os.path.join(self.AAZ_DEV_FOLDER, 'workspaces')
        super().__init__(*args, **kwargs)
        self.app = create_app()
        self.app.testing = True
        self.addCleanup(self.cleanup_dev_folder)

    def cleanup_dev_folder(self):
        if os.path.exists(self.AAZ_DEV_FOLDER):
            shutil.rmtree(self.AAZ_DEV_FOLDER)
