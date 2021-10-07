from schematics.models import Model
from schematics.types import StringType, ModelType, ListType, DictType, BooleanType, PolyModelType

from command.model.configuration import CMDHttpOperation, CMDHttpAction, CMDHttpRequest, CMDHttpRequestPath, \
    CMDHttpRequestQuery, CMDHttpRequestHeader, CMDHttpJsonBody, CMDJson
from swagger.utils import exceptions
from .external_documentation import ExternalDocumentation
from .fields import MimeField, XmsRequestIdField, XmsExamplesField, SecurityRequirementField, XPublishField, \
    XSfCodeGenField
from .parameter import ParameterField, PathParameter, QueryParameter, HeaderParameter, BodyParameter,\
    FormDataParameter, ParameterBase
from .reference import Reference, Linkable
from .response import Response
from .x_ms_long_running_operation import XmsLongRunningOperationField, XmsLongRunningOperationOptionsField
from .x_ms_odata import XmsODataField
from .x_ms_pageable import XmsPageableField


class Operation(Model, Linkable):
    """Describes a single API operation on a path."""

    tags = ListType(StringType())  # A list of tags for API documentation control. Tags can be used for logical grouping of operations by resources or any other qualifier.
    summary = StringType()  # TODO: # A short summary of what the operation does. For maximum readability in the swagger-ui, this field SHOULD be less than 120 characters.
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
    x_ms_long_running_operation_options = XmsLongRunningOperationOptionsField()  # TODO:

    x_ms_odata = XmsODataField()  # TODO: # indicates the operation includes one or more OData query parameters.
    x_ms_request_id = XmsRequestIdField()
    x_ms_examples = XmsExamplesField()  # TODO:

    # specific properties
    _x_publish = XPublishField()  # only used in Maps Data Plane
    _x_sf_codegen = XSfCodeGenField()  # only used in ServiceFabricMesh Mgmt Plane

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.x_ms_odata_instance = None

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

        for key, response in self.responses.items():
            response.link(swagger_loader, *self.traces, 'responses', key)

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

    def to_cmd_operation(self, path, method, parent_parameters, mutability):
        cmd_op = CMDHttpOperation()
        if self.x_ms_long_running_operation:
            cmd_op.long_running = True

        cmd_op.operation_id = self.operation_id
        cmd_op.description = self.description

        cmd_op.http = CMDHttpAction()
        cmd_op.http.path = path
        cmd_op.http.request = CMDHttpRequest()
        cmd_op.http.request.method = method
        cmd_op.http.responses = []

        # request
        request = cmd_op.http.request

        param_models = {}
        client_request_id_name = None
        if parent_parameters:
            for p in parent_parameters:
                model = p.to_cmd_model(mutability=mutability)
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
                model = p.to_cmd_model(mutability=mutability)
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
                request.header.params.append(model)

        if BodyParameter.IN_VALUE in param_models:
            if len(param_models[BodyParameter.IN_VALUE]) > 1:
                raise exceptions.InvalidSwaggerValueError(
                    msg="Duplicate parameters in request body",
                    key=self.traces,
                    value=[path, method, mutability, *param_models[BodyParameter.IN_VALUE].keys()]
                )
            model = [*param_models[BodyParameter.IN_VALUE].values()][0]
            if isinstance(model, CMDJson):
                request.body = CMDHttpJsonBody()
                request.body.json = model
            else:
                raise NotImplementedError()

        if FormDataParameter.IN_VALUE in param_models:
            raise NotImplementedError()

        # response
        success_responses = {}
        redirect_responses = {}
        error_responses = {}

        # convert default response
        if 'default' in self.responses:
            resp = self.responses['default']
            model = resp.to_cmd_model()
            model.is_error = True
            error_responses['default'] = (resp, model)

        for code, resp in self.responses.items():
            if code == "default":
                continue
            status_code = int(code)

            if status_code < 300:
                # success
                find_match = False
                for _, (p_resp, p_model) in success_responses.items():
                    if p_resp.schema == resp.schema:
                        p_model.status_codes.append(status_code)
                        find_match = True
                        break
                if not find_match:
                    model = resp.to_cmd_model()
                    model.status_codes = [status_code]
                    assert not model.is_error
                    success_responses[code] = (resp, model)
            elif status_code < 400:
                # redirect
                find_match = False
                for _, (p_resp, p_model) in redirect_responses.items():
                    if p_resp.schema == resp.schema:
                        p_model.status_codes.append(status_code)
                        find_match = True
                        break
                if not find_match:
                    model = resp.to_cmd_model()
                    model.status_codes = [status_code]
                    assert not model.is_error
                    redirect_responses[code] = (resp, model)
            else:
                # error
                find_match = False
                for p_code, (p_resp, p_model) in error_responses.items():
                    if p_resp.schema == resp.schema:
                        if p_code != "default":
                            p_model.status_codes.append(status_code)
                        find_match = True
                        break
                if not find_match:
                    model = resp.to_cmd_model()
                    model.status_codes = [status_code]
                    model.is_error = True
                    error_responses[code] = (resp, model)

        if len(success_responses) > 2:
            raise exceptions.InvalidSwaggerValueError(
                msg="Multi Schema for success responses",
                key=[self.traces],
                value=[*success_responses.keys()]
            )
        if len(redirect_responses) > 2:
            raise exceptions.InvalidSwaggerValueError(
                msg="Multi Schema for redirect responses",
                key=[self.traces],
                value=[*redirect_responses.keys()]
            )
        if len(error_responses) > 2:
            raise exceptions.InvalidSwaggerValueError(
                msg="Multi Schema for error responses",
                key=[self.traces],
                value=[*error_responses.keys()]
            )

        # # default response
        # if 'default' not in error_responses and len(error_responses) == 1:
        #     p_resp, p_model = [*error_responses.values()][0]
        #     if p_model.body is not None:
        #         # use the current error response as default
        #         p_model.status_codes = None
        #         error_responses = {
        #             "default": (p_resp, p_model)
        #         }
        # if 'default' not in error_responses:
        #     raise exceptions.InvalidSwaggerValueError(
        #         msg="Miss default response",
        #         key=self.traces,
        #         value=[path, method]
        #     )

        cmd_op.http.responses = []
        for _, model in success_responses.values():
            cmd_op.http.responses.append(model)
        for _, model in redirect_responses.values():
            cmd_op.http.responses.append(model)
        for _, model in error_responses.values():
            cmd_op.http.responses.append(model)
        if len(cmd_op.http.responses) == 0:
            raise exceptions.InvalidSwaggerValueError(
                msg="No http response",
                key=self.traces,
                value=[path, method]
            )
        return cmd_op
