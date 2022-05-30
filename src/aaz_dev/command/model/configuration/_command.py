import logging

from schematics.models import Model
from schematics.types import ModelType, ListType, PolyModelType

from ._arg_group import CMDArgGroup
from ._condition import CMDCondition
from ._fields import CMDDescriptionField, CMDVersionField, CMDCommandNameField
from ._operation import CMDOperation
from ._output import CMDOutput
from ._resource import CMDResource
from ._utils import CMDArgBuildPrefix, CMDDiffLevelEnum
from utils import exceptions

logger = logging.getLogger('backend')


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

    def generate_args(self):
        ref_args = []
        if self.arg_groups:
            for group in self.arg_groups:
                ref_args.extend(group.args)
        ref_args = ref_args or None

        arguments = {}
        for op in self.operations:
            for arg in op.generate_args(ref_args=ref_args):
                if arg.var not in arguments:
                    arguments[arg.var] = arg

        # check argument with duplicated option names
        dropped_args = set()
        used_args = set()
        for arg in arguments.values():
            used_args.add(arg.var)
            if arg.var in dropped_args or not arg.options:
                continue
            r_arg = None
            for v in arguments.values():
                if v.var in used_args or v.var in dropped_args or arg.var == v.var or not v.options:
                    continue
                if not set(arg.options).isdisjoint(v.options):
                    r_arg = v
                    break
            if r_arg:
                if self._can_replace_argument(r_arg, arg):
                    arg.ref_schema.arg = r_arg.var
                    dropped_args.add(arg.var)
                elif self._can_replace_argument(arg, r_arg):
                    r_arg.ref_schema.arg = arg.var
                    dropped_args.add(r_arg.var)
                else:
                    # let developer handle duplicated options
                    logger.warning(
                        f"Duplicated Option Value: {set(arg.options).intersection(r_arg.options)} : "
                        f"{arg.var} with {r_arg.var} : {self.operations[-1].operation_id}"
                    )

        arguments = [arg for var, arg in arguments.items() if var not in dropped_args]

        arg_groups = {}
        for arg in arguments:
            group_name = arg.group or ""
            if group_name not in arg_groups:
                arg_groups[group_name] = {}
            if arg.var not in arg_groups[group_name]:
                arg_groups[group_name][arg.var] = arg

        groups = []
        for group_name, args in arg_groups.items():
            group = CMDArgGroup()
            group.name = group_name
            group.args = [arg for arg in args.values()]
            groups.append(group)

        self.arg_groups = groups or None

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

    @staticmethod
    def _can_replace_argument(arg, old_arg):
        arg_prefix = arg.var.split('.')[0]
        old_prefix = old_arg.var.split('.')[0]
        if old_prefix in (CMDArgBuildPrefix.Query, CMDArgBuildPrefix.Header, CMDArgBuildPrefix.Path):
            # replace argument should only be in body
            return False
        if arg_prefix in (CMDArgBuildPrefix.Query, CMDArgBuildPrefix.Header):
            # only support path argument to replace
            return False

        elif arg_prefix == CMDArgBuildPrefix.Path:
            # path argument
            arg_schema_required = arg.ref_schema.required
            arg_schema_name = arg.ref_schema.name
            try:
                arg.ref_schema.required = old_arg.ref_schema.required
                if old_arg.ref_schema.name == "name" and "name" in arg.options:
                    arg.ref_schema.name = "name"
                diff = arg.ref_schema.diff(old_arg.ref_schema, level=CMDDiffLevelEnum.Structure)
                if diff:
                    return False
                return True
            finally:
                arg.ref_schema.name = arg_schema_name
                arg.ref_schema.required = arg_schema_required
        else:
            # body argument
            diff = arg.ref_schema.diff(old_arg.ref_schema, level=CMDDiffLevelEnum.Structure)
            if diff:
                return False
            return True
