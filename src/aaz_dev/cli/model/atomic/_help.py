from schematics.models import Model
from schematics.types import StringType, ListType, ModelType

from ._example import CLICommandExample


class CLICommandGroupHelp(Model):
    short = StringType(required=True)  # short-summary
    long = StringType()  # long-summary

    class Options:
        serialize_when_none = False


class CLICommandHelp(Model):
    short = StringType(required=True)  # short-summary
    long = StringType()  # long-summary
    examples = ListType(field=ModelType(CLICommandExample))

    class Options:
        serialize_when_none = False
