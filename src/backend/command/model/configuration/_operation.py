from schematics.models import Model
from schematics.types import PolyModelType, ModelType, ListType, StringType

from ._fields import CMDVariantField, CMDBooleanField, CMDDescriptionField
from ._http import CMDHttpAction
from ._instance_update import CMDInstanceUpdateAction


class CMDOperation(Model):
    POLYMORPHIC_KEY = None

    # properties as tags
    when = ListType(CMDVariantField())  # conditions

    class Options:
        serialize_when_none = False
        _attributes = {"when"}

    @classmethod
    def _claim_polymorphic(cls, data):
        if cls.POLYMORPHIC_KEY is None:
            return False

        if isinstance(data, dict):
            return cls.POLYMORPHIC_KEY in data
        elif isinstance(data, CMDOperation):
            return hasattr(data, cls.POLYMORPHIC_KEY)
        return False

    def generate_args(self):
        raise NotImplementedError()


class CMDHttpOperation(CMDOperation):
    POLYMORPHIC_KEY = "http"

    # properties as tags
    long_running = CMDBooleanField(
        serialized_name="longRunning",
        deserialize_from="longRunning",
    )

    operation_id = StringType(
        serialized_name="operationId",
        deserialize_from="operationId",
        required=True
    )   # OperationId from swagger

    description = CMDDescriptionField()

    # properties as nodes
    http = ModelType(CMDHttpAction, required=True)

    class Options:
        _attributes = CMDOperation.Options._attributes | {"long_running", "operation_id", "description"}

    def generate_args(self):
        return self.http.generate_args()


class CMDInstanceUpdateOperation(CMDOperation):
    POLYMORPHIC_KEY = "instanceUpdate"

    # properties as nodes
    instance_update = PolyModelType(
        CMDInstanceUpdateAction,
        allow_subclasses=True,
        required=True,
        serialized_name="instanceUpdate",
        deserialize_from="instanceUpdate"
    )

    class Options:
        _attributes = CMDOperation.Options._attributes

    def generate_args(self):
        return self.instance_update.generate_args()
