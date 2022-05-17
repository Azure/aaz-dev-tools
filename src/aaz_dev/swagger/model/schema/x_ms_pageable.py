from schematics.models import Model
from schematics.types import StringType, ModelType


class XmsPageable(Model):
    """
    The REST API guidelines define a common pattern for paging through lists of data. The operation response is modeled in OpenAPI as a list of items (a "page") and a link to the next page, effectively resembling a singly linked list. Tag the operation as x-ms-pageable and the generated code will include methods for navigating between pages.

    Note: The request to get the nextPage will always be a GET request

    https://github.com/Azure/autorest/blob/main/docs/extensions/readme.md#x-ms-pageable
    """

    item_name = StringType(
        default='value',
        serialized_name="itemName",
        deserialize_from="itemName"
    )  # Optional (default: value). Specifies the name of the property that provides the collection of pageable items.
    next_link_name = StringType(
        required=True,
        serialized_name="nextLinkName",
        deserialize_from="nextLinkName"
    )  # Specifies the name of the property that provides the next link (common: nextLink). If the model does not have a next link property then specify null. This is useful for services that return an object that has an array referenced by itemName. The object is then flattened in a way that the array is directly returned, no paging is used. This provides a better client side API to the end user.
    operation_name = StringType(
        serialized_name="operationName",
        deserialize_from="operationName"
    )  # TODO: # Optional (default: <operationName>Next). Specifies the name of the operation for retrieving the next page.


class XmsPageableField(ModelType):

    def __init__(self, **kwargs):
        super(XmsPageableField, self).__init__(
            XmsPageable,
            serialized_name='x-ms-pageable',
            deserialize_from='x-ms-pageable',
            **kwargs
        )
