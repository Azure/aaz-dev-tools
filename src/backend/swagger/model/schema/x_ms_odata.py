from .reference import ReferenceField


class XmsODataField(ReferenceField):
    """
    When present the x-ms-odata extensions indicates the operation includes one or more OData query parameters. These parameters include $filter, $top, $orderby, $skip, and $expand. In some languages the generated method will expose these parameters as strongly types OData type.

    Schema: ref to the definition that describes object used in filter.
    https://github.com/Azure/autorest/blob/main/docs/extensions/readme.md#x-ms-odata
    """

    def __init__(self, **kwargs):
        super(XmsODataField, self).__init__(
            serialized_name='x-ms-odata',
            deserialize_from='x-ms-odata',
            **kwargs
        )
