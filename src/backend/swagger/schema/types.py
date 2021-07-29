from schematics.types import StringType, DictType, ListType


# class CollectionFormatEnum(StringType):
#
#     VALID_FORMATS = ("csv", "ssv", "tsv", "pipes", "multi")
#
#     def __init__(self, additional_formats=None, **kwargs):
#         if additional_formats:
#             choices = set(*additional_formats, *self.VALID_FORMATS)
#         else:
#             choices = set(*self.VALID_FORMATS)
#         super(CollectionFormatEnum, self).__init__(
#             choices=choices, default="csv",
#             **kwargs
#         )


# class DataTypeEnum(StringType):
#
#     VALID_TYPES = ("integer", "number", "string", "boolean", "array", "file")
#
#     def __init__(self, additional_types=None, **kwargs):
#         if additional_types:
#             choices = set(*additional_types, *self.VALID_TYPES)
#         else:
#             choices = set(*self.VALID_TYPES)
#         super(DataTypeEnum, self).__init__(
#             choices=choices,
#             **kwargs
#         )


class DataTypeFormatEnum(StringType):
    VALID_TYPE_FORMATS = ("int32", "int64", "float", "double", "byte", "binary", "date", "date-time", "password")

    def __init__(self, **kwargs):
        super(DataTypeFormatEnum, self).__init__(choices=self.VALID_TYPE_FORMATS, **kwargs)


class MimeType(StringType):
    pass


class RegularExpressionType(StringType):
    # This string SHOULD be a valid regular expression
    pass


class SecurityRequirementType(DictType):
    """Lists the required security schemes to execute this operation. The object can have multiple security schemes declared in it which are all required (that is, there is a logical AND between the schemes)."""

    def __init__(self, **kwargs):
        super(SecurityRequirementType, self).__init__(
            field=ListType(StringType()), **kwargs)


class ScopesType(DictType):
    """Lists the available scopes for an OAuth2 security scheme."""

    def __init__(self, **kwargs):
        super(ScopesType, self).__init__(field=StringType(), **kwargs)
