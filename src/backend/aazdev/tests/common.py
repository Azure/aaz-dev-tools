from unittest import TestCase
from aazdev.app import create_app


class ApiTestCase(TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = create_app()
        self.app.testing = True
