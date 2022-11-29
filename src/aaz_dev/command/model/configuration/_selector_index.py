# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from schematics.models import Model
from schematics.types import StringType, ListType, ModelType, PolyModelType
from schematics.types.serializable import serializable

from ._schema import CMDSchemaField
from ._arg_builder import CMDArgBuilder


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


class CMDArrayIndex(CMDArrayIndexBase, CMDSelectorIndex):

    def generate_args(self, ref_args, var_prefix):
        if var_prefix.endswith("$"):
            var_prefix += f'{self.name}'
        else:
            var_prefix += f'.{self.name}'

        return self._generate_args_base(ref_args, var_prefix)
