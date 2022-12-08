from schematics.models import Model
from schematics.types import ListType, StringType


class CMDCommandExample(Model):
    name = StringType(required=True)
    commands = ListType(StringType(), required=True, min_size=1)
