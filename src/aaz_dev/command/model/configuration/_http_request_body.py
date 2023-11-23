from schematics.models import Model
from schematics.types import ModelType

from ._content import CMDRequestJson


class CMDHttpRequestBody(Model):
    POLYMORPHIC_KEY = None

    @classmethod
    def _claim_polymorphic(cls, data):
        if cls.POLYMORPHIC_KEY is None:
            return False

        if isinstance(data, dict):
            return cls.POLYMORPHIC_KEY in data
        elif isinstance(data, CMDHttpRequestBody):
            return hasattr(data, cls.POLYMORPHIC_KEY)

        return False

    def generate_args(self, ref_args, var_prefix=None):
        raise NotImplementedError()

    def diff(self, old, level):
        raise NotImplementedError()

    def reformat(self, **kwargs):
        return NotImplementedError()

    def register_cls(self, **kwargs):
        raise NotImplementedError()


class CMDHttpRequestJsonBody(CMDHttpRequestBody):
    POLYMORPHIC_KEY = "json"

    json = ModelType(CMDRequestJson, required=True)

    def generate_args(self, ref_args, var_prefix=None):
        return self.json.generate_args(ref_args=ref_args, var_prefix=var_prefix)

    def diff(self, old, level):
        if not isinstance(old, self.__class__):
            return f"Response type changed: '{type(old)}' != '{self.__class__}'"
        return self.json.diff(old.json, level)

    def reformat(self, **kwargs):
        self.json.reformat(**kwargs)

    def register_cls(self, **kwargs):
        self.json.register_cls(**kwargs)
