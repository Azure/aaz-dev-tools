from schematics.models import Model
from schematics.types import PolyModelType, ModelType, ListType
from ._fields import CMDVariantField
from ._http import CMDHttpAction
from ._instance_update import CMDInstanceUpdateAction


class CMDOperation(Model):
    POLYMORPHIC_KEY = None

    # properties as tags
    when = ListType(CMDVariantField())  # conditions

    @classmethod
    def _claim_polymorphic(cls, data):
        if isinstance(data, dict):
            return cls.POLYMORPHIC_KEY is not None and cls.POLYMORPHIC_KEY in data
        return False


class CMDHttpOperation(CMDOperation):
    POLYMORPHIC_KEY = "http"

    # properties as nodes
    http = ModelType(CMDHttpAction, required=True)


class CMDInstanceUpdateOperation(CMDOperation):
    POLYMORPHIC_KEY = "instance_update"

    # properties as nodes
    instance_update = PolyModelType(
        CMDInstanceUpdateAction,
        serialized_name='instanceUpdate',
        deserialize_from='instanceUpdate',
        allow_subclasses=True,
        required=True,
    )
