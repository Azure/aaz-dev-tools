import unittest

from command.model.configuration import CMDResource
from swagger.controller.command_generator import TypespecCommandGenerator
from utils.base64 import b64encode_str

PATH = "/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Mock/galleries/{galleryName}"
VERSION = "2026-03-03"


def _put_path_item():
    # Shape emitted by typespec-aaz for an ARM LRO put whose 202 repeats the resource body
    # (e.g. Microsoft.Compute galleries): the first response owns the definition and the
    # following one is a bare cls reference.
    resource_schema = {
        "type": "object",
        "cls": "Gallery_read",
        "props": [
            {"type": "string", "name": "id", "readOnly": True},
            {"type": "string", "name": "location", "required": True},
        ],
    }
    return {
        "put": {
            "operationId": "Galleries_CreateOrUpdate",
            "create": {
                "operationId": "Galleries_CreateOrUpdate",
                "http": {
                    "path": PATH,
                    "request": {
                        "method": "put",
                        "path": {"params": [
                            {"type": "string", "name": "galleryName", "required": True},
                            {"type": "string", "name": "resourceGroupName", "required": True},
                            {"type": "string", "name": "subscriptionId", "required": True},
                        ]},
                        "query": {"params": [
                            {"type": "string", "name": "api-version", "required": True},
                        ]},
                        "body": {"json": {"schema": {
                            "type": "object",
                            "name": "resource",
                            "required": True,
                            "clientFlatten": True,
                            "props": [{"type": "string", "name": "location", "required": True}],
                        }}},
                    },
                    "responses": [
                        {"statusCode": [200, 201], "body": {"json": {"schema": resource_schema}}},
                        {"statusCode": [202], "body": {"json": {"schema": {"type": "@Gallery_read"}}}},
                        {"isError": True, "body": {"json": {"schema": {
                            "readOnly": True, "type": "@MgmtErrorFormat"}}}},
                    ],
                },
            },
        },
    }


class TypespecCommandGeneratorTestCase(unittest.TestCase):

    def test_output_from_cls_reference_response(self):
        generator = TypespecCommandGenerator()
        generator.load_resources([{"path": PATH, "pathItem": _put_path_item()}])
        resource = CMDResource({
            "id": "/subscriptions/{}/resourcegroups/{}/providers/microsoft.mock/galleries/{}",
            "version": VERSION,
            "swagger": "mgmt-plane/mock/ResourceProviders/Microsoft.Mock"
                       f"/Paths/{b64encode_str(PATH)}/V/{b64encode_str(VERSION)}",
        })

        command_group = generator.create_draft_command_group(
            resource, instance_var="$Instance", methods=("put",))

        create_command = command_group.commands[0]
        self.assertEqual([output.type for output in create_command.outputs], ["object"])
