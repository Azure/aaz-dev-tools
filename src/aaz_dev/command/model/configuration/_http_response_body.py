from schematics.models import Model
from schematics.types import ModelType

from ._content import CMDResponseJson


class CMDHttpResponseBody(Model):
    POLYMORPHIC_KEY = None

    @classmethod
    def _claim_polymorphic(cls, data):
        if cls.POLYMORPHIC_KEY is None:
            return False

        if isinstance(data, dict):
            return cls.POLYMORPHIC_KEY in data
        elif isinstance(data, CMDHttpResponseBody):
            return hasattr(data, cls.POLYMORPHIC_KEY)

        return False

    def diff(self, old, level):
        raise NotImplementedError()

    def reformat(self, **kwargs):
        return NotImplementedError()

    def register_cls(self, **kwargs):
        raise NotImplementedError()


class CMDHttpResponseJsonBody(CMDHttpResponseBody):
    POLYMORPHIC_KEY = "json"

    json = ModelType(CMDResponseJson, required=True)

    def diff(self, old, level):
        if not isinstance(old, self.__class__):
            return f"Response type changed: '{type(old)}' != '{self.__class__}'"
        return self.json.diff(old.json, level)

    def reformat(self, **kwargs):
        self.json.reformat(**kwargs)

    def register_cls(self, **kwargs):
        self.json.register_cls(**kwargs)
