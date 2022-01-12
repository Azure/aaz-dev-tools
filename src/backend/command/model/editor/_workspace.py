from schematics.models import Model
from schematics.types import StringType, ModelType, UTCDateTimeType
from command.model.configuration import CMDConfiguration


class CMDEditorWorkspace(Model):

    version = UTCDateTimeType(required=True)  # this property updated when workspace saved in file.
    name = StringType(required=True)

    configuration = ModelType(CMDConfiguration, serialize_when_none=False)
