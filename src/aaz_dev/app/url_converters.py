from werkzeug.routing import BaseConverter, PathConverter

from utils.base64 import b64decode_str, b64encode_str


class Base64Converter(BaseConverter):

    def to_python(self, value: str) -> str:
        return b64decode_str(value)

    def to_url(self, value: str) -> str:
        return super(Base64Converter, self).to_url(b64encode_str(value))


class NameConverter(BaseConverter):
    regex = r"[a-z0-9]+(-[a-z0-9]+)*"


class NameWithCapitalConverter(BaseConverter):
    regex = r"[a-zA-Z0-9]+(-[a-zA-Z0-9]+)*"


class NamesPathConverter(BaseConverter):
    regex = r"[a-z0-9]+(-[a-z0-9]+)*(/[a-z0-9]+(-[a-z0-9]+)*)*"
    weight = 200

    def to_python(self, value):
        return value.split('/')

    def to_url(self, values):
        if isinstance(values, str):
            return super(NamesPathConverter, self).to_url(values)
        return '/'.join(super(NamesPathConverter, self).to_url(value) for value in values)


class ListPathConvertor(PathConverter):

    def to_python(self, value):
        return value.split('/')

    def to_url(self, values):
        if isinstance(values, str):
            return super(ListPathConvertor, self).to_url(values)
        return '/'.join(super(ListPathConvertor, self).to_url(value) for value in values)


__all__ = ["Base64Converter", "NameConverter", "NamesPathConverter", "ListPathConvertor"]
