from schematics.models import Model
from schematics.types import PolyModelType, ModelType, ListType

from ._fields import CMDVariantField, CMDBooleanField
from ._http import CMDHttpAction
from ._instance_update import CMDInstanceUpdateAction


class CMDOperation(Model):
    POLYMORPHIC_KEY = None

    # properties as tags
    when = ListType(CMDVariantField())  # conditions

    @classmethod
    def _claim_polymorphic(cls, data):
        if cls.POLYMORPHIC_KEY is None:
            return False

        if isinstance(data, dict):
            return cls.POLYMORPHIC_KEY in data
        elif isinstance(data, CMDOperation):
            return hasattr(data, cls.POLYMORPHIC_KEY)
        return False


class CMDHttpOperation(CMDOperation):
    POLYMORPHIC_KEY = "http"

    # properties as tags
    long_running = CMDBooleanField(
        serialized_name="longRunning",
        deserialize_from="longRunning",
    )

    # properties as nodes
    http = ModelType(CMDHttpAction, required=True)


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
