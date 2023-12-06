import logging

from schematics.models import Model
from schematics.types import ModelType, ListType, PolyModelType, StringType

from ._arg_group import CMDArgGroup
from ._arg import CMDClsArgBase
from ._condition import CMDCondition
from ._fields import CMDDescriptionField, CMDVersionField, CMDCommandNameField, CMDBooleanField, CMDConfirmation
from ._operation import CMDOperation, CMDHttpOperation, CMDInstanceDeleteOperation
from ._http_response_body import CMDHttpResponseJsonBody
from ._schema import CMDClsSchemaBase, CMDArraySchemaBase, CMDStringSchemaBase, CMDObjectSchemaBase
from ._output import CMDOutput, CMDArrayOutput, CMDObjectOutput, CMDStringOutput
from ._resource import CMDResource
from ._utils import CMDArgBuildPrefix, CMDDiffLevelEnum
from ._subresource_selector import CMDSubresourceSelector, CMDJsonSubresourceSelector
from ._selector_index import CMDArrayIndexBase, CMDObjectIndexBase, CMDObjectIndexDiscriminator, CMDObjectIndexAdditionalProperties
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
    subresource_selector = PolyModelType(
        CMDSubresourceSelector,
        allow_subclasses=True,
        serialized_name="subresourceSelector",
        deserialize_from="subresourceSelector"
    )
    operations = ListType(PolyModelType(CMDOperation, allow_subclasses=True), min_size=1)
    outputs = ListType(PolyModelType(CMDOutput, allow_subclasses=True), min_size=1)  # support to add outputs in different formats, such table

    confirmation = CMDConfirmation()  # support to prompt for confirmation - optional

    class Options:
        serialize_when_none = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.arg_cls_register_map = None
        self.schema_cls_register_map = None

    def generate_args(self, ref_args=None, ref_options=None):
        if not ref_args:
            ref_args = []
            if self.arg_groups:
                for group in self.arg_groups:
                    ref_args.extend(group.args)
            ref_args = ref_args or None

        arguments = {}
        has_subresource = False
        if self.subresource_selector:
            has_subresource = True
            for arg in self.subresource_selector.generate_args(ref_args=ref_args):
                if arg.var not in arguments:
                    if ref_options and arg.var in ref_options:
                        # replace generated options by ref_options
                        arg.options = [*ref_options[arg.var]]
                    arguments[arg.var] = arg

        for op in self.operations:
            for arg in op.generate_args(ref_args=ref_args, has_subresource=has_subresource):
                if arg.var not in arguments:
                    if ref_options and arg.var in ref_options:
                        # replace generated options by ref_options
                        arg.options = [*ref_options[arg.var]]
                    arguments[arg.var] = arg

        arguments = handle_duplicated_options(
            arguments, has_subresource=has_subresource, operation_id=self.operations[-1].operation_id)
        self.arg_groups = self._build_arg_groups(arguments)

    def generate_outputs(self, ref_outputs=None, pageable=None):
        if not ref_outputs:
            if self.outputs:
                ref_outputs = [*self.outputs]

        client_flatten = True
        if ref_outputs and isinstance(ref_outputs[0], (CMDArrayOutput, CMDObjectOutput)):
            client_flatten = ref_outputs[0].client_flatten

        output = None
        if self.subresource_selector:
            delete_op = False
            for op in self.operations:
                if isinstance(op, CMDInstanceDeleteOperation):
                    delete_op = True
            # instance delete action does not need output
            if not delete_op:
                output = self._build_output_type_by_subresource_selector(self.subresource_selector)
                output.ref = self.subresource_selector.var
                output.client_flatten = client_flatten
        else:
            for op in self.operations:
                if isinstance(op, CMDHttpOperation):
                    op_output = self.build_output_by_operation(op, pageable, client_flatten)
                    if op_output:
                        output = op_output

            if output and ref_outputs:
                assert len(ref_outputs) == 1, "Only support one reference output"
                ref_output = ref_outputs[0]
                if isinstance(ref_output, CMDArrayOutput) and ref_output.ref.startswith(output.ref + '.'):
                    # inherit pageable
                    output = CMDArrayOutput()
                    output.ref = ref_output.ref
                    output.next_link = ref_output.next_link
                    output.client_flatten = client_flatten

        self.outputs = [output] if output else None

    @classmethod
    def build_output_by_operation(cls, op, pageable=None, client_flatten=True):
        assert isinstance(op, CMDHttpOperation)
        output = None
        for resp in op.http.responses:
            if resp.is_error:
                continue
            if resp.body is None:
                continue
            if isinstance(resp.body, CMDHttpResponseJsonBody):
                body_json = resp.body.json
                if pageable and pageable.item_name:
                    output = CMDArrayOutput()
                    output.ref = f"{body_json.var}.{pageable.item_name}"
                    if pageable.next_link_name:
                        output.next_link = f"{body_json.var}.{pageable.next_link_name}"
                else:
                    output = cls._build_output_type_schema(body_json.schema)
                    output.ref = body_json.var
                output.client_flatten = client_flatten
            else:
                raise NotImplementedError()
        return output

    def reformat(self, **kwargs):
        self.resources = sorted(self.resources, key=lambda r: r.id)
        try:
            self._reformat_arg_groups(**kwargs)
            self._reformat_operations(**kwargs)
        except exceptions.VerificationError as err:
            err.payload['details'] = {
                "type": "Command",
                "name": self.name,
                "resources": [resource.to_primitive() for resource in self.resources],
                "details": err.payload['details']
            }
            raise err

    def _reformat_arg_groups(self, **kwargs):
        if not self.arg_groups:
            return

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

    def _reformat_operations(self, **kwargs):
        if not self.operations:
            return
        schema_cls_map = {}
        for operation in self.operations:
            operation.reformat(schema_cls_map=schema_cls_map, **kwargs)

        for key, value in schema_cls_map.items():
            if value is None:
                raise exceptions.VerificationError(
                    message=f"ReformatError: Schema Class '{key}' not defined.",
                    details=None
                )

    def link(self):
        self.arg_cls_register_map = {}
        self.schema_cls_register_map = {}

        if self.arg_groups:
            arg_cls_register_map = {}
            for arg_group in self.arg_groups:
                arg_group.register_cls(cls_register_map=arg_cls_register_map)

            for key, value in arg_cls_register_map.items():
                implement = value["implement"]
                refers = value["refers"]
                if implement is None:
                    raise exceptions.VerificationError(
                        message=f"LinkError: Argument Class '{key}' not defined.",
                        details=None
                    )
                for refer in refers:
                    assert isinstance(refer, CMDClsArgBase)
                    refer.implement = implement

            self.arg_cls_register_map = arg_cls_register_map

        if self.operations:
            schema_cls_register_map = {}
            for operation in self.operations:
                operation.register_cls(cls_register_map=schema_cls_register_map)
            for key, value in schema_cls_register_map.items():
                implement = value["implement"]
                refers = value["refers"]
                if implement is None:
                    raise exceptions.VerificationError(
                        message=f"LinkError: Schema Class '{key}' not defined.",
                        details=None
                    )
                for refer in refers:
                    assert isinstance(refer, CMDClsSchemaBase)
                    refer.implement = implement

            self.schema_cls_register_map = schema_cls_register_map

    @staticmethod
    def _build_arg_groups(arguments):
        # build argument groups
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
        return groups or None

    @staticmethod
    def _build_output_type_schema(schema):
        if isinstance(schema, CMDClsSchemaBase):
            schema = schema.implement
            assert schema is not None

        if isinstance(schema, CMDArraySchemaBase):
            output = CMDArrayOutput()
        elif isinstance(schema, CMDObjectSchemaBase):
            output = CMDObjectOutput()
        elif isinstance(schema, CMDStringSchemaBase):
            output = CMDStringOutput()
        else:
            raise exceptions.InvalidAPIUsage(
                f"Invalid output schema, not support: {schema.type}"
            )
        return output

    @staticmethod
    def _build_output_type_by_subresource_selector(subresource_selector):
        if isinstance(subresource_selector, CMDJsonSubresourceSelector):
            index = subresource_selector.json
            pref_index = None
            while index:
                pref_index = index
                index = None
                if isinstance(pref_index, CMDObjectIndexBase):
                    if pref_index.prop:
                        index = pref_index.prop
                    elif pref_index.discriminator:
                        index = pref_index.discriminator
                    elif pref_index.additional_props:
                        if pref_index.additional_props.item:
                            index = pref_index.additional_props.item
                elif isinstance(pref_index, CMDObjectIndexDiscriminator):
                    if pref_index.prop:
                        index = pref_index.prop
                    elif pref_index.discriminator:
                        index = pref_index.discriminator
                elif isinstance(pref_index, CMDArrayIndexBase):
                    if pref_index.item:
                        index = pref_index.item
                else:
                    raise NotImplementedError()
            if isinstance(pref_index, (CMDObjectIndexBase, CMDObjectIndexDiscriminator)):
                output = CMDObjectOutput()
            elif isinstance(pref_index, CMDArrayIndexBase):
                output = CMDArrayOutput()
        else:
            raise NotImplementedError()
        return output


def handle_duplicated_options(arguments, has_subresource, operation_id):
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
            # check whether you need to replace argument
            if _can_replace_argument(r_arg, arg, has_subresource):
                arg.ref_schema.arg = r_arg.var
                dropped_args.add(arg.var)
            elif _can_replace_argument(arg, r_arg, has_subresource):
                r_arg.ref_schema.arg = arg.var
                dropped_args.add(r_arg.var)
            else:
                # warning developer handle duplicated options
                logger.warning(
                    f"Duplicated Option Value: {set(arg.options).intersection(r_arg.options)} : "
                    f"{arg.var} with {r_arg.var} : {operation_id}"
                )

    return [arg for var, arg in arguments.items() if var not in dropped_args]


def _can_replace_argument(arg, old_arg, has_subresource):
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
        if has_subresource:
            return False

        arg_schema_required = arg.ref_schema.required
        arg_schema_name = arg.ref_schema.name
        try:
            # temporary assign required and name for diff
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
