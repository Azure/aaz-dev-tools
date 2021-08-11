from schematics.models import Model
from schematics.types import StringType, ModelType


class XmsPageable(Model):
    """
    The REST API guidelines define a common pattern for paging through lists of data. The operation response is modeled in OpenAPI as a list of items (a "page") and a link to the next page, effectively resembling a singly linked list. Tag the operation as x-ms-pageable and the generated code will include methods for navigating between pages.

    Note: The request to get the nextPage will always be a GET request

    https://github.com/Azure/autorest/blob/main/docs/extensions/readme.md#x-ms-pageable
    """

    itemName = StringType(default='value')  # Optional (default: value). Specifies the name of the property that provides the collection of pageable items.
    nextLinkName = StringType(required=True)  # Specifies the name of the property that provides the next link (common: nextLink). If the model does not have a next link property then specify null. This is useful for services that return an object that has an array referenced by itemName. The object is then flattened in a way that the array is directly returned, no paging is used. This provides a better client side API to the end user.
    operationName = StringType()  # Optional (default: <operationName>Next). Specifies the name of the operation for retrieving the next page.
