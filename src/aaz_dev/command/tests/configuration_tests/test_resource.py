from unittest import TestCase
from command.model.configuration._resource import *


class ResourceTest(TestCase):

    def test_resource(self):
        resource = CMDResource({
            "id": "/subscriptions/{}/resourcegroups/{}/providers/microsoft.insights/datacollectionrules/{}",
            "version": "2021-04-01",
        })

        resource.validate()
        resource.to_native()
        resource.to_primitive()
