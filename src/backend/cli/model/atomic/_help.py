from cli.model.atomic._example import CLICommandExample
from schematics.models import Model
from schematics.types import StringType, ListType, ModelType


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
