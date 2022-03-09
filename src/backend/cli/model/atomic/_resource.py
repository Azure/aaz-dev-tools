from cli.model.atomic._fields import CLIResourceIdField, CLIVersionField
from schematics.models import Model
from utils.fields import PlaneField


class CLISpecsResource(Model):
    plane = PlaneField(required=True)
    id = CLIResourceIdField(required=True)
    version = CLIVersionField(required=True)

    class Options:
        serialize_when_none = False
