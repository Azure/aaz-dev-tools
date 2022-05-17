from schematics.models import Model
from schematics.types import ModelType, DictType, StringType

from ._profile import CLIAtomicProfile


class CLIModule(Model):
    name = StringType(required=True)
    folder = StringType()
    profiles = DictType(
        field=ModelType(CLIAtomicProfile),
    )

    class Options:
        serialize_when_none = False
