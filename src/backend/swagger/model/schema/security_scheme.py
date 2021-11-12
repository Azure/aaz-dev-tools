from schematics.models import Model
from schematics.types import StringType, URLType, PolyModelType
from .fields import ScopesField


class _SecuritySchemeBase(Model):
    """Allows the definition of a security scheme that can be used by the operations. Supported schemes are basic authentication, an API key (either as a header or as a query parameter) and OAuth2's common flows (implicit, password, application and access code)."""

    TYPE_VALUE = None

    type = StringType(choices=("basic", "apiKey", "oauth2"), required=True)
    description = StringType()

    @classmethod
    def _claim_polymorphic(cls, data):
        if isinstance(data, dict):
            type_value = data.get('type', None)
            return type_value is not None and type_value == cls.TYPE_VALUE
        elif isinstance(data, _SecuritySchemeBase):
            return data.TYPE_VALUE == cls.TYPE_VALUE
        return False


class BasicSecurityScheme(_SecuritySchemeBase):
    TYPE_VALUE = "basic"


class APIKeySecurityScheme(_SecuritySchemeBase):
    TYPE_VALUE = "apiKey"

    name = StringType(required=True)  # The name of the header or query parameter to be used.
    in_ = StringType(
        choices=("query", "header"),
        required=True,
        serialized_name="in",
        deserialize_from="in"
    )  # The location of the API key. Valid values are "query" or "header".


class OAuth2SecurityScheme(_SecuritySchemeBase):
    TYPE_VALUE = "oauth2"

    flow = StringType(choices=("implicit", "password", "application", "accessCode"), required=True)  # The flow used by the OAuth2 security scheme.
    authorization_url = URLType(
        serialized_name="authorizationUrl",
        deserialize_from="authorizationUrl"
    )  # The authorization URL to be used for this flow. oauth2 ("implicit", "accessCode")
    token_url = URLType(
        serialized_name="tokenUrl",
        deserialize_from="tokenUrl"
    )  # The token URL to be used for this flow. oauth2 ("password", "application", "accessCode")
    scopes = ScopesField()  # The available scopes for the OAuth2 security scheme.


class SecuritySchemeField(PolyModelType):

    def __init__(self, **kwargs):
        model_spec = [
            BasicSecurityScheme, APIKeySecurityScheme, OAuth2SecurityScheme
        ]
        super(SecuritySchemeField, self).__init__(model_spec=model_spec, **kwargs)

