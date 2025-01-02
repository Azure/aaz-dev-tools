from schematics.models import Model
from schematics.types import StringType, ListType, ModelType
from ._resource_provider import PSSketchResourceProvider

class PSSketchProfile(Model):

    resource_providers = ListType(
        field=ModelType(PSSketchResourceProvider),
        serialized_name="resourceProviders",
        deserialize_from="resourceProviders",
    )

    class Options:
        serialize_when_none = False


