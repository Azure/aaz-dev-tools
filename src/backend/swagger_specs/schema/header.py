from schematics.models import Model
from schematics.types import StringType
from .items import Items
from .types import XmsHeaderCollectionPrefixType


class Header(Items):
    description = StringType()     # A short description of the header.

    x_ms_header_collection_prefix = XmsHeaderCollectionPrefixType()  # Handle collections of arbitrary headers by distinguishing them with a specified prefix.
