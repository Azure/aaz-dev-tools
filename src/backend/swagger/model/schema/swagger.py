from schematics.models import Model
from schematics.types import StringType, ModelType, ListType, DictType
from schematics.exceptions import ValidationError
from .info import Info
from .path_item import PathsType, XmsPathsType
from .schema import Schema
from .parameter import ParameterType
from .response import Response
from .tag import Tag
from .external_documentation import ExternalDocumentation
from .security_scheme import SecuritySchemeType
from .types import SecurityRequirementType, MimeType
from .x_ms_parameterized_host import XmsParameterizedHostType


def _swagger_version_validator(v):
    if v != "2.0":
        raise ValidationError(f"Only Support Swagger '2.0': Current value is '{v}'")


class Swagger(Model):
    """
    This is the root document object for the API specification. It combines what previously was the Resource Listing and API Declaration (version 1.2 and earlier) together into one document.
    """

    swagger = StringType(validators=[_swagger_version_validator], default="2.0", required=True)  # Specifies the Swagger Specification version being used. It can be used by the Swagger UI and other clients to interpret the API listing. The value MUST be "2.0".
    info = ModelType(Info, required=True)  # Provides metadata about the API. The metadata can be used by the clients if needed.
    host = StringType()  # The host (name or ip) serving the API. This MUST be the host only and does not include the scheme nor sub-paths. It MAY include a port. If the host is not included, the host serving the documentation is to be used (including the port). The host does not support path templating.
    basePath = StringType()  # The base path on which the API is served, which is relative to the host. If it is not included, the API is served directly under the host. The value MUST start with a leading slash (/). The basePath does not support path templating.
    schemes = ListType(StringType(choices=("http", "https", "ws", "wss")))  # The transfer protocol of the API. Values MUST be from the list: "http", "https", "ws", "wss". If the schemes is not included, the default scheme to be used is the one used to access the Swagger definition itself.
    consumes = ListType(MimeType())  # A list of MIME types the APIs can consume. This is global to all APIs but can be overridden on specific API calls. Value MUST be as described under Mime Types.
    produces = ListType(MimeType())  # A list of MIME types the APIs can produce. This is global to all APIs but can be overridden on specific API calls. Value MUST be as described under Mime Types.
    paths = PathsType(required=True)  # The available paths and operations for the API.
    definitions = DictType(ModelType(Schema))  # An object to hold data types produced and consumed by operations.
    parameters = DictType(ParameterType(support_reference=False))  # An object to hold parameters that can be used across operations. This property does not define global parameters for all operations.
    responses = DictType(ModelType(Response))  # An object to hold responses that can be used across operations. This property does not define global responses for all operations.
    securityDefinitions = DictType(SecuritySchemeType())  # Security scheme definitions that can be used across the specification.
    security = ListType(SecurityRequirementType())  # A declaration of which security schemes are applied for the API as a whole. The list of values describes alternative security schemes that can be used (that is, there is a logical OR between the security requirements). Individual operations can override this definition.
    tags = ListType(ModelType(Tag))  # A list of tags used by the specification with additional metadata. The order of the tags can be used to reflect on their order by the parsing tools. Not all tags that are used by the Operation Object must be declared. The tags that are not declared may be organized randomly or based on the tools' logic. Each tag name in the list MUST be unique.
    externalDocs = ModelType(ExternalDocumentation)  # Additional external documentation.

    x_ms_paths = XmsPathsType()  # alternative to Paths Object that allows Path Item Object to have query parameters for non pure REST APIs
    x_ms_parameterized_host = XmsParameterizedHostType()

    def unfold(self, ref_loader):
        pass

