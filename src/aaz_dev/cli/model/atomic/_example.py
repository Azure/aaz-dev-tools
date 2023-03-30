from schematics.models import Model
from schematics.types import StringType, ListType


class CLICommandExample(Model):
    name = StringType(required=True)
    commands = ListType(StringType(), required=True, min_size=1)

    class Options:
        serialize_when_none = False
