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
        try:
            if self.arg_groups:
                used_options = set()
                args_in_group = {}
                for arg_group in self.arg_groups:
                    for arg in arg_group.args:
                        group_name = arg.group or ""
                        if group_name not in args_in_group:
                            args_in_group[group_name] = []
                        args_in_group[group_name].append(arg)
                        for option in arg.options:
                            if option in used_options:
                                raise exceptions.VerificationError(
                                    message=f"Argument option '{option}' duplicated.",
                                    details={
                                        "type": "Argument",
                                        "options": arg.options,
                                        "var": arg.var,
                                    }
                                )
                            used_options.add(option)
                arg_groups = []
                for group_name, args in args_in_group.items():
                    arg_group = CMDArgGroup()
                    arg_group.name = group_name
                    arg_group.args = args
                    arg_group.reformat(**kwargs)
                    arg_groups.append(arg_group)
                self.arg_groups = sorted(arg_groups, key=lambda a: a.name)

            if self.operations:
                schema_cls_map = {}
                for operation in self.operations:
                    operation.reformat(schema_cls_map=schema_cls_map, **kwargs)

                for key, value in schema_cls_map.items():
                    if value is None:
                        raise exceptions.VerificationError(
                            message=f"Schema Class '{key}' not defined.",
                            details=None
                        )
        except exceptions.VerificationError as err:
            err.payload['details'] = {
                "type": "Command",
                "name": self.name,
                "resources": [resource.to_primitive() for resource in self.resources],
                "details": err.payload['details']
            }
            raise err
