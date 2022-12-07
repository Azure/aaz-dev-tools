from cli.model.common._fields import CLIResourceIdField, CLIVersionField
from schematics.models import Model
from schematics.types import StringType
from utils.fields import PlaneField


class CLISpecsResource(Model):
    plane = PlaneField(required=True)
    id = CLIResourceIdField(required=True)
    version = CLIVersionField(required=True)
    subresource = StringType()  # subresource index, used for sub commands generation.

    class Options:
        serialize_when_none = False
