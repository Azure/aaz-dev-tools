import logging
from urllib.parse import urljoin

from schematics.models import Model
from schematics.types import StringType, ModelType, ListType, DictType, BooleanType, PolyModelType

from command.model.configuration import CMDHttpOperation, CMDHttpAction, CMDHttpRequest, CMDHttpRequestPath, \
    CMDHttpRequestQuery, CMDHttpRequestHeader, CMDHttpRequestJsonBody, CMDRequestJson, CMDHttpOperationLongRunning
from swagger.utils import exceptions
from swagger.utils.tools import swagger_resource_path_to_resource_id_template
from .example_item import XmsExamplesField
from .external_documentation import ExternalDocumentation
from .fields import MimeField, XmsRequestIdField, SecurityRequirementField, XPublishField, \
    XSfCodeGenField, XmsClientNameField
from .parameter import ParameterField, PathParameter, QueryParameter, HeaderParameter, BodyParameter,\
    FormDataParameter, ParameterBase
from .reference import Reference, Linkable
from .response import Response
from .schema import ReferenceSchema
from .x_ms_long_running_operation import XmsLongRunningOperationField, XmsLongRunningOperationOptionsField
from .x_ms_odata import XmsODataField
from .x_ms_pageable import XmsPageableField

logger = logging.getLogger('backend')


class Operation(Model, Linkable):
    """Describes a single API operation on a path."""

    tags = ListType(StringType())  # A list of tags for API documentation control. Tags can be used for logical grouping of operations by resources or any other qualifier.
    summary = StringType()  # A short summary of what the operation does. For maximum readability in the swagger-ui, this field SHOULD be less than 120 characters.
    description = StringType()  # A verbose explanation of the operation behavior. GFM syntax can be used for rich text representation.
    external_docs = ModelType(
        ExternalDocumentation,
        serialized_name="externalDocs",
        deserialize_from="externalDocs"
    )  # TODO: # Additional external documentation for this operation.
    operation_id = StringType(
        serialized_name="operationId",
        deserialize_from="operationId",
    )  # Unique string used to identify the operation. The id MUST be unique among all operations described in the API. Tools and libraries MAY use the operationId to uniquely identify an operation, therefore, it is recommended to follow common programming naming conventions.
    consumes = ListType(MimeField())  # TODO: # A list of MIME types the operation can consume. This overrides the consumes definition at the Swagger Object. An empty value MAY be used to clear the global definition. Value MUST be as described under Mime Types.
    produces = ListType(MimeField())  # TODO: # A list of MIME types the operation can produce. This overrides the produces definition at the Swagger Object. An empty value MAY be used to clear the global definition. Value MUST be as described under Mime Types.
    parameters = ListType(ParameterField(support_reference=True))  # A list of parameters that are applicable for this operation. If a parameter is already defined at the Path Item, the new definition will override it, but can never remove it. The list MUST NOT include duplicated parameters. A unique parameter is defined by a combination of a name and location. The list can use the Reference Object to link to parameters that are defined at the Swagger Object's parameters. There can be one "body" parameter at most.
    responses = DictType(PolyModelType([
        Reference, Response
    ]), required=True)  # The list of possible responses as they are returned from executing this operation.
    schemes = ListType(StringType(
        choices=("http", "https", "ws", "wss")
    ))  # TODO: # The transfer protocol for the operation. Values MUST be from the list: "http", "https", "ws", "wss". The value overrides the Swagger Object schemes definition.
    deprecated = BooleanType(default=False)  # TODO: # Declares this operation to be deprecated. Usage of the declared operation should be refrained. Default value is false.
    security = ListType(SecurityRequirementField())  # TOOD: # A declaration of which security schemes are applied for this operation. The list of values describes alternative security schemes that can be used (that is, there is a logical OR between the security requirements). This definition overrides any declared top-level security. To remove a top-level security declaration, an empty array can be used.

    x_ms_pageable = XmsPageableField()  # TODO:
    x_ms_long_running_operation = XmsLongRunningOperationField(default=False)
    x_ms_long_running_operation_options = XmsLongRunningOperationOptionsField()

    x_ms_odata = XmsODataField()  # TODO: # indicates the operation includes one or more OData query parameters.
    x_ms_request_id = XmsRequestIdField()
    x_ms_examples = XmsExamplesField()

    # specific properties
    _x_publish = XPublishField()  # only used in Maps Data Plane
    _x_sf_codegen = XSfCodeGenField()  # only used in ServiceFabricMesh Mgmt Plane
    _x_ms_client_name = XmsClientNameField()  # only used in Maps Data Plane

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.x_ms_odata_instance = None
        self.x_ms_lro_final_state_schema = None

    def link(self, swagger_loader, *traces):
        if self.is_linked():
            return
        super().link(swagger_loader, *traces)

        if self.parameters is not None:
            for idx, param in enumerate(self.parameters):
                if isinstance(param, Linkable):
                    param.link(swagger_loader, *self.traces, 'parameters', idx)

            # replace parameter reference by parameter instance
            for idx in range(len(self.parameters)):
                param = self.parameters[idx]
                while isinstance(param, Reference):
                    param = param.ref_instance
                assert isinstance(param, ParameterBase)
                self.parameters[idx] = param

        # current response

        # verify path is resource id template or not
        resource_id_template = None
        if self.traces[-1] == 'get':
            # path should support get method
            resource_path = self.traces[-2]
            resource_id_template = swagger_resource_path_to_resource_id_template(resource_path)

        for key, response in self.responses.items():
            if resource_id_template and key != "default" and int(key) < 300:
                response.link(
                    swagger_loader, *self.traces, 'responses', key,
                    resource_id_template=resource_id_template
                )
            else:
                response.link(
                    swagger_loader, *self.traces, 'responses', key
                )

        # replace response reference by response instance
        for key in [*self.responses.keys()]:
            resp = self.responses[key]
            while isinstance(resp, Reference):
                if resp.ref_instance is None:
                    raise exceptions.InvalidSwaggerValueError(
                        msg="Reference not exist",
                        key=[],
                        value=resp.ref
                    )
                resp = resp.ref_instance
            assert isinstance(resp, Response)
            self.responses[key] = resp

        if self.x_ms_odata is not None:
            self.x_ms_odata_instance, instance_traces = swagger_loader.load_ref(
                self.x_ms_odata, *self.traces, 'x_ms_odata')
            if isinstance(self.x_ms_odata_instance, Linkable):
                self.x_ms_odata_instance.link(swagger_loader, *instance_traces)

        if self.x_ms_long_running_operation_options is not None and \
                self.x_ms_long_running_operation_options.final_state_schema is not None:
            # `final-state-schema` to `$ref`
            self.x_ms_lro_final_state_schema = ReferenceSchema()
            self.x_ms_lro_final_state_schema.ref = self.x_ms_long_running_operation_options.final_state_schema
            self.x_ms_lro_final_state_schema.link(
                swagger_loader,
                *self.traces, "x_ms_long_running_operation_options", "final_state_schema"
            )

        if self.x_ms_examples is not None:
            for key, example in self.x_ms_examples.items():
                try:
                    example.link(swagger_loader, *self.traces, "x_ms_examples", key)
                except Exception as e:
                    logger.error(f"Link example failed: {e}: {key}.")

    def to_cmd(self, builder, parent_parameters, host_path, **kwargs):
        cmd_op = CMDHttpOperation()
        if self.x_ms_long_running_operation:
            cmd_op.long_running = CMDHttpOperationLongRunning()
            if self.x_ms_long_running_operation_options:
                cmd_op.long_running.final_state_via = self.x_ms_long_running_operation_options.final_state_via

        cmd_op.operation_id = self.operation_id
        builder.setup_description(cmd_op, self)

        cmd_op.http = CMDHttpAction()
        if host_path:
            cmd_op.http.path = host_path + builder.path
        else:
            cmd_op.http.path = builder.path
        cmd_op.http.request = CMDHttpRequest()
        cmd_op.http.request.method = builder.method
        cmd_op.http.responses = []

        # request
        request = cmd_op.http.request

        param_models = {}
        client_request_id_name = None
        if parent_parameters:
            for p in parent_parameters:
                model = builder(p)
                if model is None:
                    continue
                if p.IN_VALUE not in param_models:
                    param_models[p.IN_VALUE] = {}
                param_models[p.IN_VALUE][p.name] = model
                if p.IN_VALUE == HeaderParameter.IN_VALUE:
                    if p.x_ms_client_request_id or p.name == "x-ms-client-request-id":
                        client_request_id_name = p.name

        if self.parameters:
            for p in self.parameters:
                model = builder(p)
                if model is None:
                    continue
                if p.IN_VALUE not in param_models:
                    param_models[p.IN_VALUE] = {}
                param_models[p.IN_VALUE][p.name] = model
                if p.IN_VALUE == HeaderParameter.IN_VALUE:
                    if p.x_ms_client_request_id or p.name == "x-ms-client-request-id":
                        client_request_id_name = p.name

        if PathParameter.IN_VALUE in param_models:
            request.path = CMDHttpRequestPath()
            request.path.params = []
            for _, model in sorted(param_models[PathParameter.IN_VALUE].items()):
                request.path.params.append(model)

        if QueryParameter.IN_VALUE in param_models:
            request.query = CMDHttpRequestQuery()
            request.query.params = []
            for _, model in sorted(param_models[QueryParameter.IN_VALUE].items()):
                request.query.params.append(model)

        if HeaderParameter.IN_VALUE in param_models:
            request.header = CMDHttpRequestHeader()
            request.header.client_request_id = client_request_id_name
            request.header.params = []
            for name, model in sorted(param_models[HeaderParameter.IN_VALUE].items()):
                if name == client_request_id_name:
                    # ignore client request id parameter for argument generation.
                    continue
                request.header.params.append(model)

        if BodyParameter.IN_VALUE in param_models:
            if len(param_models[BodyParameter.IN_VALUE]) > 1:
                raise exceptions.InvalidSwaggerValueError(
                    msg="Duplicate parameters in request body",
                    key=self.traces,
                    value=[builder.path, builder.method, builder.mutability, *param_models[BodyParameter.IN_VALUE].keys()]
                )
            model = [*param_models[BodyParameter.IN_VALUE].values()][0]
            if isinstance(model, CMDRequestJson):
                request.body = CMDHttpRequestJsonBody()
                request.body.json = model
            else:
                raise NotImplementedError()

        if FormDataParameter.IN_VALUE in param_models:
            raise NotImplementedError()

        # response
        success_responses,  redirect_responses, error_responses = builder.classify_responses(self)

        cmd_op.http.responses = []
        for status_codes, resp in success_responses:
            model = builder(resp, status_codes=status_codes)
            cmd_op.http.responses.append(model)
        for status_codes, resp in redirect_responses:
            model = builder(resp, status_codes=status_codes)
            cmd_op.http.responses.append(model)
        for status_codes, resp in error_responses:
            model = builder(resp, is_error=True, status_codes=status_codes)
            cmd_op.http.responses.append(model)

        if len(cmd_op.http.responses) == 0:
            raise exceptions.InvalidSwaggerValueError(
                msg="No http response",
                key=self.traces,
                value=[builder.path, builder.method]
            )
        return cmd_op
