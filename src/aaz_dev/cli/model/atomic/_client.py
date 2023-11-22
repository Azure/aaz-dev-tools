from cli.model.common._fields import CLIClientConfigField
from schematics.models import Model
from schematics.types import StringType
from utils.fields import PlaneField


class CLIAtomicClient(Model):

    plane = PlaneField(required=True)
    name = StringType(required=True)  # client name registered in azure-cli-core, it will include the plane name and currently module name
    registered_name = StringType(
        required=True,
        serialized_name="registeredName",
        deserialize_from="registeredName"
    )
    cls_name = StringType(
        required=True,
        serialized_name="clsName",
        deserialize_from="clsName",
    )
    cfg = CLIClientConfigField()

    class Options:
        serialize_when_none = False
