from schematics.models import Model
from schematics.types import DictType, ModelType

from command.model.configuration import CMDCommandExample
from .reference import Linkable, ReferenceField


class ExampleItem(Model, Linkable):
    ref = ReferenceField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ref_instance = None

    def link(self, swagger_loader, *traces):
        if self.is_linked():
            return

        super().link(swagger_loader, *traces)

        self.ref_instance, instance_traces = swagger_loader.load_ref(self.ref, *self.traces, "ref")

    def to_cmd(self, builder, cmd_name, **kwargs):
        if not self.ref_instance:
            return

        params = builder.mapping(self.ref_instance.get("parameters", {}))

        command = cmd_name
        for k, v in params.items():
            command += f" --{k} {v}"
            # command += " --" + k + " " + v

        return CMDCommandExample({"commands": [command.strip()]})


class XmsExamplesField(DictType):
    """
    Describes the format for specifying examples for request and response of an operation in an OpenAPI definition.
    It is a dictionary of different variations of the examples for a given operation.

    https://github.com/Azure/azure-rest-api-specs/blob/master/documentation/x-ms-examples.md
    """
    def __init__(self, **kwargs):
        super().__init__(
            field=ModelType(ExampleItem),
            serialized_name="x-ms-examples",
            deserialize_from="x-ms-examples",
            **kwargs
        )
