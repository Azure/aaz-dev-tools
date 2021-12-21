from schematics.models import Model
from schematics.types import ModelType

from ._content import CMDJson


class CMDHttpBody(Model):
    POLYMORPHIC_KEY = None

    class Options:
        _attributes = set()

    @classmethod
    def _claim_polymorphic(cls, data):
        if cls.POLYMORPHIC_KEY is None:
            return False

        if isinstance(data, dict):
            return cls.POLYMORPHIC_KEY in data
        elif isinstance(data, CMDHttpBody):
            return hasattr(data, cls.POLYMORPHIC_KEY)

        return False

    def generate_args(self):
        raise NotImplementedError()


class CMDHttpJsonBody(CMDHttpBody):
    POLYMORPHIC_KEY = "json"

    json = ModelType(CMDJson, required=True)

    class Options:
        _attributes = CMDHttpBody.Options._attributes

    def generate_args(self):
        return self.json.generate_args()
