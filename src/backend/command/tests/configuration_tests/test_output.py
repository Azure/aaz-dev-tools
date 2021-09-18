from unittest import TestCase
from command.model.configuration._output import *


class OutputTest(TestCase):

    def test_object_output(self):
        output = CMDObjectOutput({
            "type": "object",
            "ref": "$instance.property",
            "clientFlatten": True
        })
        output.validate()
        print(output.to_native())
        print(output.to_primitive())

    def test_array_output(self):
        output = CMDArrayOutput({
            "type": "array<object>",
            "ref": "$instance.value",
            "nextLink": "$instance.nextLink",
            "clientFlatten": True
        })
        output.validate()
        print(output.to_native())
        print(output.to_primitive())

    def test_string_output(self):
        output = CMDStringOutput({
            "type": "string",
            "value": "delete success",
        })
        output.validate()
        print(output.to_native())
        print(output.to_primitive())
