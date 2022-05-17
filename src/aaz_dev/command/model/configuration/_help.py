from schematics.models import Model
from schematics.types import StringType, ListType


class CMDHelp(Model):
    # properties as tags
    short = StringType(required=True)  # short-summary

    # properties as nodes
    lines = ListType(StringType())  # long-summary separated by lines

    class Options:
        serialize_when_none = False


class CMDArgumentHelp(CMDHelp):
    # properties as nodes
    ref_commands = ListType(
        StringType(),
        serialized_name='refCommands',
        deserialize_from='refCommands',
    )  # popular commands
