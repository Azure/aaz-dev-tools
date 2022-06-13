from schematics.types import StringType
from .items import Items
from .fields import XmsClientNameField, XmsHeaderCollectionPrefix


class Header(Items):
    description = StringType()     # A short description of the header.

    x_ms_client_name = XmsClientNameField()

    # specific properties, will not support
    x_ms_header_collection_prefix = XmsHeaderCollectionPrefix()  # only used in Storage Data plane
