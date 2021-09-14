from schematics.types import StringType, BaseType
from enum import Enum


class CMDStageEnum(str, Enum):
    Experimental = "Experimental"
    Preview = "Preview"
    Stable = "Stable"


class CMDStageField(StringType):
    """The stage for command group, command or argument."""

    def __init__(self, *args, **kwargs):
        super(CMDStageField, self).__init__(
            choices=(CMDStageEnum.Experimental, CMDStageEnum.Preview, CMDStageEnum.Stable),
            default=CMDStageEnum.Stable,
            *args,
            **kwargs
        )


class CMDVariantField(StringType):
    """The variant definition"""

    def __init__(self, *args, **kwargs):
        super(CMDVariantField, self).__init__(
            regex=r'\$[a-zA-Z0-9_\[\]\.]+',
            *args,
            **kwargs
        )


class CMDTypeField(StringType):
    """
    Base type: "array", "boolean", "integer", "number", "object", "string"
    """

    def __init__(self, *args, **kwargs):
        super(CMDTypeField, self).__init__(
            serialized_name='type',
            deserialize_from='type',
            *args, **kwargs
        )


class CMDSchemaClassField(StringType):

    def __init__(self, *args, **kwargs):
        super(CMDSchemaClassField, self).__init__(
            regex=r'\@[a-zA-Z0-9_]+',
            *args, **kwargs
        )


class CMDJsonValueField(BaseType):
    """
    Can parse json value format string, the result type can be None, integer, float, bool, string, list or dict
    """

    def __init__(self, *args, **kwargs):
        super(CMDJsonValueField, self).__init__(*args, **kwargs)


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
