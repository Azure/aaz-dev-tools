from schematics.types import StringType
from .items import Items
from .fields import XmsClientNameField


class Header(Items):
    description = StringType()     # A short description of the header.

    x_ms_client_name = XmsClientNameField()
