from schematics.models import Model
from schematics.types import ModelType, ListType, PolyModelType, StringType
from utils.fields import PlaneField, CloudField
from ._arg import CMDArg

from ._schema import CMDSchemaField


class CMDClientAADAuthConfig(Model):
    scopes = ListType(StringType, required=True)

    class Options:
        serialize_when_none = False


class CMDClientAuth(Model):
    aad_token = ModelType(
        CMDClientAADAuthConfig,
        serialized_name='AADToken',
        deserialize_from='AADToken',
    )

    class Options:
        serialize_when_none = False


class CMDClientEndpoint(Model):
    cloud = CloudField(required=True)
    template = StringType(required=True)
    
    # parameters used in template. They should be the same across all endpoints.
    params = ListType(CMDSchemaField())

    class Options:
        serialize_when_none = False


class CMDClientConfig(Model):

    plane = PlaneField(required=True)
    endpoints = ListType(ModelType(CMDClientEndpoint), required=True)
    auth = ModelType(CMDClientAuth, required=True)
    args = ListType(PolyModelType(CMDArg, allow_subclasses=True))

    class Options:
        serialize_when_none = False
