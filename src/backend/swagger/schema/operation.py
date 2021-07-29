from schematics.models import Model
from schematics.types import StringType, ModelType, ListType, DictType, BooleanType
from .external_documentation import ExternalDocumentation
from .parameter import ParameterType
from .response import Response
from .security_requirement import SecurityRequirementType
from .types import MimeType


class Operation(Model):
    """Describes a single API operation on a path."""

    tags = ListType(StringType(), serialize_when_none=False)  # A list of tags for API documentation control. Tags can be used for logical grouping of operations by resources or any other qualifier.
    summary = StringType(serialize_when_none=False)     # A short summary of what the operation does. For maximum readability in the swagger-ui, this field SHOULD be less than 120 characters.
    description = StringType(serialize_when_none=False)  # A verbose explanation of the operation behavior. GFM syntax can be used for rich text representation.
    externalDocs = ModelType(ExternalDocumentation, serialize_when_none=False)  # Additional external documentation for this operation.
    operationId = StringType(serialize_when_none=False)  # Unique string used to identify the operation. The id MUST be unique among all operations described in the API. Tools and libraries MAY use the operationId to uniquely identify an operation, therefore, it is recommended to follow common programming naming conventions.
    consumes = ListType(MimeType(), serialize_when_none=False)  # A list of MIME types the operation can consume. This overrides the consumes definition at the Swagger Object. An empty value MAY be used to clear the global definition. Value MUST be as described under Mime Types.
    produces = ListType(MimeType(), serialize_when_none=False)  # A list of MIME types the operation can produce. This overrides the produces definition at the Swagger Object. An empty value MAY be used to clear the global definition. Value MUST be as described under Mime Types.
    parameters = ListType(ParameterType(support_reference=True), serialize_when_none=False)  # A list of parameters that are applicable for this operation. If a parameter is already defined at the Path Item, the new definition will override it, but can never remove it. The list MUST NOT include duplicated parameters. A unique parameter is defined by a combination of a name and location. The list can use the Reference Object to link to parameters that are defined at the Swagger Object's parameters. There can be one "body" parameter at most.
    responses = DictType(ModelType(Response), required=True)  # The list of possible responses as they are returned from executing this operation.
    schemes = ListType(StringType(choices=("http", "https", "ws", "wss")), serialize_when_none=False)  # The transfer protocol for the operation. Values MUST be from the list: "http", "https", "ws", "wss". The value overrides the Swagger Object schemes definition.
    deprecated = BooleanType(serialize_when_none=False, default=False)  # Declares this operation to be deprecated. Usage of the declared operation should be refrained. Default value is false.
    security = ListType(SecurityRequirementType(), serialize_when_none=False)  # A declaration of which security schemes are applied for this operation. The list of values describes alternative security schemes that can be used (that is, there is a logical OR between the security requirements). This definition overrides any declared top-level security. To remove a top-level security declaration, an empty array can be used.
