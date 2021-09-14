from schematics.models import Model
from schematics.types import ModelType
from ._schema import CMDJson


class CMDHttpBody(Model):
    POLYMORPHIC_KEY = None

    @classmethod
    def _claim_polymorphic(cls, data):
        if isinstance(data, dict):
            return cls.POLYMORPHIC_KEY is not None and cls.POLYMORPHIC_KEY in data
        return False


class CMDHttpJsonBody(CMDHttpBody):
    POLYMORPHIC_KEY = "json"

    json = ModelType(CMDJson, required=True)
