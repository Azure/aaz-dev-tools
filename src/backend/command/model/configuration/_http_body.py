from schematics.models import Model
from schematics.types import PolyModelType
from ._schema import CMDJson


class CMDHttpBody(Model):
    POLYMORPHIC_KEY = None

    @classmethod
    def _claim_polymorphic(cls, data):
        if cls.POLYMORPHIC_KEY is None:
            return False

        if isinstance(data, dict):
            return cls.POLYMORPHIC_KEY in data
        elif isinstance(data, CMDHttpBody):
            return hasattr(data, cls.POLYMORPHIC_KEY)


class CMDHttpJsonBody(CMDHttpBody):
    POLYMORPHIC_KEY = "json"

    json = PolyModelType(CMDJson, allow_subclasses=True, required=True)
