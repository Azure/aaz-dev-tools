from unittest import TestCase

from command.model.configuration._resource import *


class ResourceTest(TestCase):

    def test_resource(self):
        resource = CMDResource({
            "id": "/{resourceid}/providers/microsoft.changeanalysis/resourcechanges",
            "version": "2021-04-01",
            "swagger": "mgmt-plane/changeanalysis/ResourceProviders/Microsoft.ChangeAnalysis/Paths/L3tyZXNvdXJjZUlkfS9wcm92aWRlcnMvTWljcm9zb2Z0LkNoYW5nZUFuYWx5c2lzL3Jlc291cmNlQ2hhbmdlcw==/V/MjAyMS0wNC0wMQ=="
        })

        resource.validate()
        resource.to_native()
        resource.to_primitive()
