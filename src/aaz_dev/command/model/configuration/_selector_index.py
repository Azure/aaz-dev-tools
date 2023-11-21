# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from schematics.models import Model
from schematics.types import StringType, ListType, ModelType, PolyModelType
from schematics.types.serializable import serializable

from ._schema import CMDSchemaField, CMDStringSchemaBase, CMDStringSchema
from ._arg_builder import CMDArgBuilder
from ._utils import CMDDiffLevelEnum


class CMDSelectorIndexBase(Model):
    TYPE_VALUE = None

    class Options:
        serialize_when_none = False

    @serializable
    def type(self):
        return self._get_type()

    def generate_args(self, ref_args, var_prefix):
        raise NotImplementedError()

    def reformat(self, **kwargs):
        raise NotImplementedError()

    def _get_type(self):
        assert self.TYPE_VALUE is not None
        return self.TYPE_VALUE

    @classmethod
    def _claim_polymorphic(cls, data):
        if cls.TYPE_VALUE is None:
            return False

        if isinstance(data, dict):
            type_value = data.get('type', None)
            if type_value is not None:
                typ = type_value.replace("<", " ").replace(">", " ").strip().split()[0]
                return typ == cls.TYPE_VALUE
        elif isinstance(data, CMDSelectorIndexBase):
            return data.TYPE_VALUE == cls.TYPE_VALUE
        return False

    def _diff_base(self, old, level, diff):
        return diff

    def diff(self, old, level):
        if type(self) is not type(old):
            return f"Type: {type(old)} != {type(self)}"
        diff = {}
        diff = self._diff_base(old, level, diff)
        return diff


class CMDSelectorIndexBaseField(PolyModelType):

    def __init__(self, **kwargs):
        super(CMDSelectorIndexBaseField, self).__init__(
            model_spec=CMDSelectorIndexBase,
            allow_subclasses=True,
            serialize_when_none=False,
            **kwargs
        )

    def find_model(self, data):
        if self.claim_function:
            kls = self.claim_function(self, data)
            if not kls:
                raise Exception("Input for polymorphic field did not match any model")
            return kls

        fallback = None
        matching_classes = set()
        for kls in self._get_candidates():
            if issubclass(kls, CMDSelectorIndex):
                continue

            try:
                kls_claim = kls._claim_polymorphic
            except AttributeError:
                if not fallback:
                    fallback = kls
            else:
                if kls_claim(data):
                    matching_classes.add(kls)

        if not matching_classes and fallback:
            return fallback
        elif len(matching_classes) != 1:
            raise Exception("Got ambiguous input for polymorphic field")

        return matching_classes.pop()


class CMDSelectorIndex(CMDSelectorIndexBase):
    # properties as tags
    name = StringType(required=True)

    @classmethod
    def _claim_polymorphic(cls, data):
        if super(CMDSelectorIndex, cls)._claim_polymorphic(data):
            if isinstance(data, dict):
                # distinguish with CMDSchemaBase and CMDSchema
                return 'name' in data
            else:
                return isinstance(data, CMDSelectorIndex)
        return False

    def _diff(self, old, level, diff):
        if level >= CMDDiffLevelEnum.BreakingChange:
            if self.name != old.name:
                diff["name"] = f"{old.name} != {self.name}"
        return diff

    def diff(self, old, level):
        if type(self) is not type(old):
            return f"Type: {type(old)} != {type(self)}"
        diff = {}
        diff = self._diff_base(old, level, diff)
        diff = self._diff(old, level, diff)
        return diff


class CMDSelectorIndexField(PolyModelType):

    def __init__(self, **kwargs):
        super(CMDSelectorIndexField, self).__init__(
            model_spec=CMDSelectorIndex,
            allow_subclasses=True,
            serialize_when_none=False,
            **kwargs
        )

# object


class CMDObjectIndexDiscriminator(Model):
    # properties as tags
    property = StringType(required=True)
    value = StringType(required=True)

    # properties as nodes
    prop = CMDSelectorIndexField()
    discriminator = ModelType('CMDObjectIndexDiscriminator')

    class Options:
        serialize_when_none = False

    def generate_args(self, ref_args, var_prefix):
        if var_prefix.endswith("$"):
            var_prefix += f'{self.value}'
        else:
            var_prefix += f'.{self.value}'

        args = []
        if self.prop:
            args.extend(self.prop.generate_args(ref_args, var_prefix))
        if self.discriminator:
            args.extend(self.discriminator.generate_args(ref_args, var_prefix))

        return args

    def diff(self, old, level):
        diff = {}
        if level >= CMDDiffLevelEnum.BreakingChange:
            if self.property != old.property:
                diff["property"] = f"{old.property} != {self.property}"
            if self.value != old.value:
                diff["value"] = f"{old.value} != {self.value}"

            if (not self.prop) != (not old.prop):
                diff["prop"] = f"New prop" if self.prop else f"Miss prop"
            elif self.prop:
                if prop_diff := self.prop.diff(old.prop, level):
                    diff["prop"] = prop_diff

            if (not self.discriminator) != (not old.discriminator):
                diff["discriminator"] = f"New discriminator" if self.discriminator else f"Miss discriminator"
            elif self.discriminator:
                if disc_diff := self.discriminator.diff(old.discriminator, level):
                    diff["discriminator"] = disc_diff
        return diff

    def reformat(self, **kwargs):
        if self.prop:
            self.prop.reformat(**kwargs)
        if self.discriminator:
            self.discriminator.reformat(**kwargs)


class CMDObjectIndexAdditionalProperties(Model):
    item = CMDSelectorIndexBaseField(required=True)
    identifiers = ListType(CMDSchemaField())

    class Options:
        serialize_when_none = False

    def generate_args(self, ref_args, var_prefix):
        args = []
        if self.identifiers:
            for identifier in self.identifiers:
                builder = CMDArgBuilder.new_builder(schema=identifier, ref_args=ref_args, var_prefix=var_prefix)
                identifier_args = builder.get_args()
                assert len(identifier_args) == 1
                args.append(identifier_args[0])

        var_prefix += '{}'
        args.extend(self.item.generate_args(ref_args, var_prefix))
        return args
    
    def diff(self, old, level):
        diff = {}
        if level >= CMDDiffLevelEnum.BreakingChange:
            if diff_item := self.item.diff(old.item):
                diff['item'] = diff_item
        identifiers_diff = _diff_identifiers(
            self.identifiers or [],
            old.identifiers or [],
            level
        )
        if identifiers_diff:
            diff["identifiers"] = identifiers_diff
        return diff

    def reformat(self, **kwargs):
        if self.item:
            self.item.reformat(**kwargs)
        if self.identifiers:
            for identifier in self.identifiers:
                identifier.reformat(**kwargs)
            self.identifiers = sorted(self.identifiers, key=lambda i: i.name)


class CMDObjectIndexBase(CMDSelectorIndexBase):
    TYPE_VALUE = "object"

    prop = CMDSelectorIndexField()
    discriminator = ModelType(CMDObjectIndexDiscriminator)
    additional_props = ModelType(
        CMDObjectIndexAdditionalProperties,
        serialized_name="additionalProps",
        deserialize_from="additionalProps",
    )

    def _generate_args_base(self, ref_args, var_prefix):
        args = []
        if self.prop:
            args.extend(self.prop.generate_args(ref_args, var_prefix))
        if self.discriminator:
            args.extend(self.discriminator.generate_args(ref_args, var_prefix))
        if self.additional_props:
            args.extend(self.additional_props.generate_args(ref_args, var_prefix))
        return args

    def generate_args(self, ref_args, var_prefix):
        return self._generate_args_base(ref_args, var_prefix)

    def reformat(self, **kwargs):
        if self.prop:
            self.prop.reformat(**kwargs)
        if self.discriminator:
            self.discriminator.reformat(**kwargs)
        if self.additional_props:
            self.additional_props.reformat(**kwargs)

    def _diff_base(self, old, level, diff):
        if level >= CMDDiffLevelEnum.BreakingChange:
            if (not self.prop) != (not old.prop):
                diff['prop'] = f"New prop" if self.prop else f"Miss prop"
            elif self.prop:
                if prop_diff := self.prop.diff(old.prop, level):
                    diff["prop"] = prop_diff
            
            if (not self.discriminator) != (not old.discriminator):
                diff['discriminator'] = f"New discriminator" if self.discriminator else f"Miss discriminator"
            elif self.discriminator:
                if discriminator_diff := self.discriminator.diff(old.discriminator, level):
                    diff["discriminator"] = discriminator_diff

            if (not self.additional_props) != (not old.additional_props):
                diff['additional_props'] = f"New additional_props" if self.additional_props else f"Miss additional_props"
            elif self.additional_props:
                if additional_props_diff := self.additional_props.diff(old.additional_props, level):
                    diff["additional_props"] = additional_props_diff
        return diff


class CMDObjectIndex(CMDObjectIndexBase, CMDSelectorIndex):

    def generate_args(self, ref_args, var_prefix):
        if var_prefix.endswith("$"):
            var_prefix += f'{self.name}'
        else:
            var_prefix += f'.{self.name}'

        return self._generate_args_base(ref_args, var_prefix)

# array


class CMDArrayIndexBase(CMDSelectorIndexBase):
    TYPE_VALUE = "array"

    item = CMDSelectorIndexBaseField()
    identifiers = ListType(CMDSchemaField())

    def _generate_args_base(self, ref_args, var_prefix):
        args = []
        if self.identifiers:
            for identifier in self.identifiers:
                builder = CMDArgBuilder.new_builder(schema=identifier, ref_args=ref_args, var_prefix=var_prefix)
                identifier_args = builder.get_args()
                assert len(identifier_args) == 1
                args.append(identifier_args[0])

        var_prefix += "[]"
        if self.item:
            args.extend(self.item.generate_args(ref_args, var_prefix))

        return args

    def generate_args(self, ref_args, var_prefix):
        return self._generate_args_base(ref_args, var_prefix)

    def reformat(self, **kwargs):
        if self.item:
            self.item.reformat(**kwargs)
        if self.identifiers:
            for identifier in self.identifiers:
                identifier.reformat(**kwargs)
            self.identifiers = sorted(self.identifiers, key=lambda i: i.name)
    
    def _diff_base(self, old, level, diff):
        if level >= CMDDiffLevelEnum.BreakingChange:
            if (not self.item) != (not old.item):
                diff['item'] = f"New item" if self.item else f"Miss item"
            elif self.item:
                if item_diff := self.item.diff(old.item, level):
                    diff["item"] = item_diff
        identifiers_diff = _diff_identifiers(
            self.identifiers or [],
            old.identifiers or [],
            level
        )
        if identifiers_diff:
            diff["identifiers"] = identifiers_diff
        return diff


class CMDArrayIndex(CMDArrayIndexBase, CMDSelectorIndex):

    def generate_args(self, ref_args, var_prefix):
        if var_prefix.endswith("$"):
            var_prefix += f'{self.name}'
        else:
            var_prefix += f'.{self.name}'

        return self._generate_args_base(ref_args, var_prefix)


# simple type index, used to select base types such as string, number, boolean, etc.
class CMDSimpleIndexBase(CMDSelectorIndexBase):
    TYPE_VALUE = "simple"

    supported_schema_types = (CMDStringSchemaBase,)

    def _generate_args_base(self, ref_args, var_prefix):
        return []

    def generate_args(self, ref_args, var_prefix):
        return self._generate_args_base(ref_args, var_prefix)

    def reformat(self, **kwargs):
        pass

    def _diff_base(self, old, level, diff):
        return diff


class CMDSimpleIndex(CMDSimpleIndexBase, CMDSelectorIndex):

    supported_schema_types = (CMDStringSchema,)

    pass


def _diff_identifiers(self_identifiers, old_identifiers, level):
    identifiers_diff = {}
    if level >= CMDDiffLevelEnum.BreakingChange:
        identifiers_dict = {identifier.name: identifier for identifier in self_identifiers}
        for old_identifier in old_identifiers:
            if old_identifier.name not in identifiers_dict:
                identifiers_diff[old_identifier.name] = "Miss identifier"
            else:
                identifier = identifiers_dict.pop(old_identifier.name)
                diff = identifier.diff(old_identifier, level)
                if diff:
                    identifiers_diff[old_identifier.name] = diff
        
        for identifier in identifiers_dict.values():
            identifiers_diff[identifier.name] = "New identifier"
    
    return identifiers_diff
