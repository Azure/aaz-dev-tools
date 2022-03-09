from schematics.types import StringType, BaseType, BooleanType
from utils.stage import AAZStageEnum, AAZStageField


class CMDBooleanField(BooleanType):

    def __init__(self, **kwargs):
        super(CMDBooleanField, self).__init__(serialize_when_none=False, default=False, **kwargs)

    def to_native(self, value, context=None):
        value = super(CMDBooleanField, self).to_native(value, context)
        if value is False:
            return None  # return None when value is false to hide field with `serialize_when_none=False`
        return value

    def to_primitive(self, value, context=None):
        value = super(CMDBooleanField, self).to_primitive(value, context)
        if value is False:
            return None  # return None when value is false to hide field with `serialize_when_none=False`
        return value


class CMDStageField(AAZStageField):
    """The stage for command group, command or argument."""

    def to_native(self, value, context=None):
        value = super(CMDStageField, self).to_native(value, context)
        if value == AAZStageEnum.Stable:
            return None  # return None when value is false to hide field with `serialize_when_none=False`
        return value

    def to_primitive(self, value, context=None):
        value = super(CMDStageField, self).to_primitive(value, context)
        if value == AAZStageEnum.Stable:
            return None  # return None when value is false to hide field with `serialize_when_none=False`
        return value


class CMDVariantField(StringType):
    """The variant definition"""

    def __init__(self, *args, **kwargs):
        super(CMDVariantField, self).__init__(
            regex=r'\$[a-zA-Z0-9_\[\]\.]+',
            *args,
            **kwargs
        )


class CMDClassField(StringType):

    def __init__(self, *args, **kwargs):
        super(CMDClassField, self).__init__(
            regex=r'\@[a-zA-Z0-9_]+',
            *args, **kwargs
        )


class CMDPrimitiveField(BaseType):
    """
    Can parse json value format string, the result type can be None, integer, float, bool, string, list or dict
    """

    def __init__(self, *args, **kwargs):
        super(CMDPrimitiveField, self).__init__(
            serialize_when_none=True,
            *args, **kwargs,
        )


class CMDRegularExpressionField(StringType):
    # This string SHOULD be a valid regular expression
    pass


class CMDVersionField(StringType):

    def __init__(self, *args, **kwargs):
        super(CMDVersionField, self).__init__(*args, **kwargs)


class CMDResourceIdField(StringType):

    def __init__(self, *args, **kwargs):
        super(CMDResourceIdField, self).__init__(
            serialized_name='id',
            deserialize_from='id',
            *args, **kwargs
        )


class CMDCommandNameField(StringType):

    def __init__(self, *args, **kwargs):
        super(CMDCommandNameField, self).__init__(
            regex=r'^[a-z0-9]+(-[a-z0-9]+)*$',
            min_length=1, *args, **kwargs)


class CMDCommandGroupNameField(StringType):

    def __init__(self, *args, **kwargs):
        super(CMDCommandGroupNameField, self).__init__(
            regex=r'^[a-z0-9]+(-[a-z0-9]+)*( [a-z0-9]+(-[a-z0-9]+)*)*$',
            min_length=1, *args, **kwargs)


class CMDURLPathField(StringType):

    def __init__(self, *args, **kwargs):
        super(CMDURLPathField, self).__init__(*args, **kwargs)


class CMDDescriptionField(StringType):
    """The description information from swagger. It's the source of helps. Should not be saved in configuration file."""

    def __init__(self, *args, **kwargs):
        super(CMDDescriptionField, self).__init__(
            serialize_when_none=False,
            *args,
            **kwargs
        )

    def to_primitive(self, value, context=None):
        """the description will not exist when call to primitive"""
        return None  # return None when value is false to hide field with `serialize_when_none=False`
