from schematics.models import Model
from schematics.types import ModelType, ListType, PolyModelType

from ._arg_group import CMDArgGroup
from ._condition import CMDCondition
from ._fields import CMDDescriptionField, CMDVersionField, CMDCommandNameField
from ._operation import CMDOperation
from ._output import CMDOutput
from ._resource import CMDResource
from utils import exceptions


class CMDCommand(Model):
    # properties as tags
    name = CMDCommandNameField(required=True)
    version = CMDVersionField(required=True)

    description = CMDDescriptionField()

    # properties as nodes
    resources = ListType(ModelType(CMDResource), min_size=1)  # the azure resources used in this command
    arg_groups = ListType(
        ModelType(CMDArgGroup),
        serialized_name='argGroups',
        deserialize_from='argGroups',
    )
    conditions = ListType(ModelType(CMDCondition))
    operations = ListType(PolyModelType(CMDOperation, allow_subclasses=True), min_size=1)
    outputs = ListType(PolyModelType(CMDOutput, allow_subclasses=True), min_size=1)  # support to add outputs in different formats, such table

    class Options:
        serialize_when_none = False

    def reformat(self, **kwargs):
        self.resources = sorted(self.resources, key=lambda r: r.id)
        if self.arg_groups:
            for arg_group in self.arg_groups:
                arg_group.reformat(**kwargs)
            self.arg_groups = sorted(self.arg_groups, key=lambda a: a.name)
        if self.operations:
            schema_cls_map = {}
            for operation in self.operations:
                operation.reformat(schema_cls_map=schema_cls_map, **kwargs)
            for key, value in schema_cls_map.items():
                if value is None:
                    raise exceptions.VerificationError(
                        message=f"Schema Class '{key}' not defined.",
                        details={
                            "name": self.name,
                            "resources": [resource.to_primitive() for resource in self.resources]
                        }
                    )
