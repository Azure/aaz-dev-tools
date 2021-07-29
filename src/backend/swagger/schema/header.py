from schematics.models import Model
from schematics.types import StringType
from .items import Items


class Header(Items):
    description = StringType(serialize_when_none=False)     # A short description of the header.
