import {
  HttpOperation,
  HttpPayloadBody,
  HttpOperationResponse,
  HttpStatusCodeRange,
  HttpStatusCodesEntry,
  Visibility,
  createMetadataInfo,
  getHeaderFieldOptions,
  getServers,
  getStatusCodeDescription,
  getVisibilitySuffix,
  resolveRequestVisibility,
  HttpProperty,
} from "@typespec/http";
import { isAzureResource } from "@azure-tools/typespec-azure-resource-manager";
import { AAZEmitterContext, AAZOperationEmitterContext, AAZSchemaEmitterContext } from "./context.js";
import { resolveOperationId, toCamelCase } from "./utils.js";
import { TypeSpecPathItem } from "./model/path_item.js";
import { CMDHttpOperation } from "./model/operation.js";
import {
  DiagnosticTarget,
  Enum,
  EnumMember,
  Model,
  ModelProperty,
  Namespace,
  Program,
  Scalar,
  Type,
  Union,
  Value,
  getDiscriminator,
  getDoc,
  getEncode,
  getFormat,
  getMaxItems,
  getMaxLength,
  getMaxValue,
  getMaxValueExclusive,
  getMinItems,
  getMinLength,
  getMinValue,
  getMinValueExclusive,
  getPattern,
  getPagingOperation,
  getProperty,
  isArrayModelType,
  isNeverType,
  isNullType,
  isRecordModelType,
  isService,
  isTemplateDeclaration,
  isVoidType,
  resolveEncodedName,
  IntrinsicType,
  serializeValueAsJson,
} from "@typespec/compiler";
import { TwoLevelMap } from "@typespec/compiler/utils";
import {
  LroMetadata,
  UnionEnum,
  getArmResourceIdentifierConfig,
  getLroMetadata,
  getUnionAsEnum,
} from "@azure-tools/typespec-azure-core";
import { XmsPageable } from "./model/x_ms_pageable.js";
import { CMDHttpRequest, CMDHttpResponse } from "./model/http.js";
import {
  CMDArraySchemaBase,
  CMDClsSchema,
  CMDClsSchemaBase,
  CMDObjectSchema,
  CMDObjectSchemaBase,
  CMDSchema,
  CMDSchemaBase,
  CMDStringSchema,
  CMDStringSchemaBase,
  CMDIntegerSchemaBase,
  Ref,
  ClsType,
  ArrayType,
  CMDObjectSchemaDiscriminator,
  CMDByteSchemaBase,
  CMDInteger32SchemaBase,
  CMDInteger64SchemaBase,
  CMDFloatSchemaBase,
  CMDFloat64SchemaBase,
  CMDFloat32SchemaBase,
  CMDUuidSchemaBase,
  CMDPasswordSchemaBase,
  CMDResourceIdSchemaBase,
  CMDDateSchemaBase,
  CMDDateTimeSchemaBase,
  CMDDurationSchemaBase,
  CMDResourceLocationSchema,
  CMDIdentityObjectSchemaBase,
  CMDBooleanSchemaBase,
  CMDAnyTypeSchemaBase,
} from "./model/schema.js";
import { reportDiagnostic } from "./lib.js";
import { getExtensions, getOpenAPITypeName, isReadonlyProperty } from "@typespec/openapi";
import { getMaxProperties, getMinProperties, getMultipleOf, getUniqueItems } from "@typespec/json-schema";
import { shouldFlattenProperty } from "@azure-tools/typespec-client-generator-core";
import {
  CMDArrayFormat,
  CMDFloatFormat,
  CMDIntegerFormat,
  CMDObjectFormat,
  CMDResourceIdFormat,
  CMDStringFormat,
} from "./model/format.js";

interface DiscriminatorInfo {
  propertyName: string;
  value: string;
}

export function retrieveAAZOperation(
  context: AAZEmitterContext,
  operation: HttpOperation,
  pathItem: TypeSpecPathItem | undefined,
): TypeSpecPathItem {
  context.tracer.trace("RetrieveOperation", `${operation.verb} ${operation.path}`);
  if (!pathItem) {
    pathItem = {};
  }

  const verb = operation.verb;
  const opId = resolveOperationId(context, operation);
  if (!pathItem[verb]) {
    pathItem[verb] = {};
  }
  pathItem[verb]!.operationId = opId;
  pathItem[verb]!.pageable = extractPagedMetadata(context.program, operation);

  const metadateInfo = createMetadataInfo(context.program, {
    canonicalVisibility: Visibility.Read,
  });
  const typeNameOptions = {
    // shorten type names by removing TypeSpec and service namespace
    namespaceFilter(ns: Namespace) {
      return !isService(context.program, ns);
    },
  };
  const opContext: AAZOperationEmitterContext = {
    ...context,
    typeNameOptions,
    metadateInfo,
    operationId: opId,
    visibility: Visibility.Read,
    pendingSchemas: new TwoLevelMap(),
    refs: new TwoLevelMap(),
  };
  const verbVisibility = resolveRequestVisibility(context.program, operation.operation, verb);
  if (verb === "get") {
    opContext.visibility = Visibility.Query;
    pathItem[verb]!.read = convert2CMDOperation(opContext, operation);
    processPendingSchemas(opContext, verbVisibility, "read");
  } else if (verb === "head") {
    opContext.visibility = Visibility.Query;
    pathItem[verb]!.read = convert2CMDOperation(opContext, operation);
    processPendingSchemas(opContext, verbVisibility, "read");
  } else if (verb === "delete") {
    opContext.visibility = Visibility.Delete;
    pathItem[verb]!.create = convert2CMDOperation(opContext, operation);
    processPendingSchemas(opContext, verbVisibility, "create");
  } else if (verb === "post") {
    opContext.visibility = Visibility.Create;
    pathItem[verb]!.create = convert2CMDOperation(opContext, operation);
    processPendingSchemas(opContext, verbVisibility, "create");
  } else if (verb === "put") {
    opContext.visibility = Visibility.Create;
    pathItem[verb]!.create = convert2CMDOperation(opContext, operation);
    processPendingSchemas(opContext, verbVisibility, "create");
    opContext.visibility = Visibility.Update;
    opContext.pendingSchemas.clear();
    opContext.refs.clear();
    pathItem[verb]!.update = convert2CMDOperation(opContext, operation);
    processPendingSchemas(opContext, verbVisibility, "update");
  } else if (verb === "patch") {
    opContext.visibility = Visibility.Update;
    pathItem[verb]!.update = convert2CMDOperation(opContext, operation);
    processPendingSchemas(opContext, verbVisibility, "update");
  } else {
    console.log(" verb not expected: ", verb);
  }
  return pathItem;
}

function convert2CMDOperation(context: AAZOperationEmitterContext, operation: HttpOperation): CMDHttpOperation {
  // TODO: resolve host parameters for the operation
  const hostPathAndParameters = extractHostPathAndParameters(context);
  const hostPath = hostPathAndParameters?.hostPath ?? "";
  const op: CMDHttpOperation = {
    operationId: context.operationId,
    description: getDoc(context.program, operation.operation),
    http: {
      // merge host path and operation path
      path: hostPath + getPathWithoutQuery(operation.path),
    },
  };

  let lroMetadata = getLroMetadata(context.program, operation.operation);
  if (operation.verb === "get") {
    lroMetadata = undefined;
  }
  if (lroMetadata !== undefined && operation.verb !== "get") {
    op.longRunning = {
      finalStateVia: lroMetadata.finalStateVia,
    };
    // TODO: add support for custom polling information
  }

  op.http.request = extractHttpRequest(context, operation, hostPathAndParameters?.hostParameters ?? {});
  op.http.responses = extractHttpResponses(
    {
      ...context,
      visibility: Visibility.Read,
    },
    operation,
    lroMetadata,
  );
  return op;
}

function extractHostPathAndParameters(
  context: AAZOperationEmitterContext,
): { hostPath: string; hostParameters: Record<string, CMDSchema> } | undefined {
  const servers = getServers(context.program, context.service.type);
  if (servers === undefined || servers.length > 1) {
    return undefined;
  }
  const server = servers[0];
  // using r"^(.*://)?[^/]*(/.*)$" to split server url into host and path if url matches the pattern else the path should be empty
  const hostPath = server.url.match(/^(.*:\/\/[^/]+)?(\/.*)$/)?.[2] ?? "";
  if (hostPath === "/" || hostPath === "") {
    return undefined;
  }
  // using r"\{([^{}]*)}" to iterate over all parameter names in hostPath, the name should not contain '{' or '}'
  const hostParameters: Record<string, CMDSchema> = {};
  const hostPathParameters = hostPath.matchAll(/\{([^{}]*)\}/g);
  for (const match of hostPathParameters) {
    const name = match[1];
    const param = server.parameters?.get(name);
    let schema;
    if (param === undefined) {
      reportDiagnostic(context.program, {
        code: "missing-host-parameter",
        target: context.service.type,
        message: `Host parameter '${name}' is not defined in the server parameters.`,
      });
    } else {
      schema = convert2CMDSchema(
        {
          ...context,
          visibility: Visibility.Read,
          supportClsSchema: false,
        },
        param,
        name,
      );
    }
    if (schema === undefined) {
      schema = {
        name,
        type: "string",
      };
    }
    schema.required = true;
    hostParameters[name] = schema;
  }

  return {
    hostPath,
    hostParameters,
  };
}

function extractHttpRequest(
  context: AAZOperationEmitterContext,
  operation: HttpOperation,
  hostParameters: Record<string, CMDSchema>,
): CMDHttpRequest | undefined {
  const request: CMDHttpRequest = {
    method: operation.verb,
  };

  let schemaContext;
  const methodParams = operation.parameters;
  const paramModels: Record<string, Record<string, CMDSchema>> = {};
  // add host parameters from the host path to path parameters
  if (hostParameters && Object.keys(hostParameters).length > 0) {
    paramModels["path"] = {
      ...hostParameters,
    };
  }

  let clientRequestIdName;
  for (const httpProperty of methodParams.properties) {
    if (!["header", "query", "path"].includes(httpProperty.kind)) {
      continue;
    }
    schemaContext = buildSchemaEmitterContext(context, httpProperty);
    const schema = convert2CMDSchema(
      schemaContext,
      httpProperty.property,
      "options" in httpProperty ? httpProperty.options.name : "",
    );
    if (!schema) {
      continue;
    }

    schema.required = !httpProperty.property.optional;

    if (paramModels[httpProperty.kind] === undefined) {
      paramModels[httpProperty.kind] = {};
    }
    paramModels[httpProperty.kind][schema.name] = schema;
    if (httpProperty.kind === "header" && schema.name === "x-ms-client-request-id") {
      clientRequestIdName = schema.name;
    }
  }

  if (paramModels["path"]) {
    request.path = {
      params: [],
    };
    // sort by param name
    for (const name of Object.keys(paramModels["path"]).sort()) {
      request.path.params!.push(paramModels["path"][name]);
    }
  }

  if (paramModels["query"]) {
    request.query = {
      params: [],
    };
    // sort by param name
    for (const name of Object.keys(paramModels["query"]).sort()) {
      request.query.params!.push(paramModels["query"][name]);
    }
  }

  if (paramModels["header"]) {
    request.header = {
      params: [],
    };
    // sort by param name
    for (const name of Object.keys(paramModels["header"]).sort()) {
      if (name === clientRequestIdName) {
        continue;
      }
      request.header.params!.push(paramModels["header"][name]);
    }
    if (clientRequestIdName) {
      request.header.clientRequestId = clientRequestIdName;
    }
  }

  if (methodParams.body && !isVoidType(methodParams.body.type)) {
    const body = methodParams.body!;
    const consumes: string[] = body.contentTypes ?? [];
    if (consumes.length === 0) {
      // we didn't find an explicit content type anywhere, so infer from body.
      if (getModelOrScalarTypeIfNullable(body.type)) {
        consumes.push("application/json");
      }
    }
    if (body.bodyKind === "multipart") {
      throw new Error("NotImplementedError: Multipart form data payloads are not supported.");
    }
    if (isBinaryPayload(body.type, consumes)) {
      throw new Error("NotImplementedError: Binary payloads are not supported.");
    }
    if (consumes.includes("multipart/form-data")) {
      throw new Error("NotImplementedError: Multipart form data payloads are not supported.");
    }

    let schema: CMDSchema | undefined;
    if (body.property) {
      context.tracer.trace("RetrieveBody", context.visibility.toString());
      schema = convert2CMDSchema(
        {
          ...context,
          supportClsSchema: true,
        },
        body.property,
        getJsonName(context, body.property),
      )!;
      schema.required = !body.property.optional;
    } else {
      schema = {
        ...convert2CMDSchemaBase(
          {
            ...context,
            supportClsSchema: true,
          },
          body.type,
        )!,
        name: "body",
        required: true,
      };
    }
    if (schema !== undefined) {
      // schema.required = !methodParams.body.type.optional;
      if (schema.type === "object") {
        schema = {
          ...schema,
          clientFlatten: true,
        } as CMDObjectSchema;
      }
      request.body = {
        json: {
          schema,
        },
      };
    }
  }
  return request;
}

function extractHttpResponses(
  context: AAZOperationEmitterContext,
  operation: HttpOperation,
  lroMetadata: LroMetadata | undefined,
): CMDHttpResponse[] | undefined {
  let success202Response: CMDHttpResponse | undefined; // only one success 202 response is allowed
  let success204Response: CMDHttpResponse | undefined; // only one success 204 response is allowed
  let success2xxResponse: CMDHttpResponse | undefined; // only one success 2xx(except 202 and 204) response is allowed
  let redirectResponse: CMDHttpResponse | undefined;
  const errorResponses = [];

  for (const response of operation.responses) {
    let statusCodes = getOpenAPI2StatusCodes(context, response.statusCodes, response.type);
    if (statusCodes.length === 0) {
      reportDiagnostic(context.program, {
        code: "missing-status-codes",
        target: response.type,
      });
    }
    if (statusCodes.includes("default")) {
      errorResponses.push(convert2CMDHttpResponse(context, response, undefined, true));
      continue;
    }
    const isSuccess = statusCodes.map((code) => code.startsWith("2")).includes(true);
    const isRedirect = statusCodes.map((code) => code.startsWith("3")).includes(true);
    const isError = !isSuccess && !isRedirect;
    if (isSuccess) {
      if (statusCodes.includes("202")) {
        if (success202Response !== undefined) {
          reportDiagnostic(context.program, {
            code: "Duplicated-success-202",
            target: response.type,
          });
        }
        success202Response = convert2CMDHttpResponse(context, response, ["202"], false);
      }
      if (statusCodes.includes("204")) {
        if (success204Response !== undefined) {
          reportDiagnostic(context.program, {
            code: "Duplicated-success-204",
            target: response.type,
          });
        }
        success204Response = convert2CMDHttpResponse(context, response, ["204"], false);
      }
      // remove 202 and 204 from statusCodes
      statusCodes = statusCodes.filter((code) => code !== "202" && code !== "204");
      if (statusCodes.length > 0) {
        if (success2xxResponse !== undefined) {
          success2xxResponse.statusCode = [
            ...success2xxResponse.statusCode!,
            ...statusCodes.map((code) => Number(code)),
          ];
          context.tracer.trace("AppendSuccess2xxStatusCodes", JSON.stringify(success2xxResponse.statusCode));
        } else {
          success2xxResponse = convert2CMDHttpResponse(context, response, statusCodes, false);
        }
      }
    } else if (isRedirect) {
      if (redirectResponse !== undefined) {
        reportDiagnostic(context.program, {
          code: "Duplicated-redirect",
          target: response.type,
        });
      }
      redirectResponse = convert2CMDHttpResponse(context, response, statusCodes, false);
    } else if (isError) {
      errorResponses.push(convert2CMDHttpResponse(context, response, statusCodes, true));
    }
  }

  const responses = [];
  if (success2xxResponse !== undefined) {
    responses.push(success2xxResponse);
  }
  if (success202Response !== undefined) {
    responses.push(success202Response);
  }
  if (success204Response !== undefined) {
    responses.push(success204Response);
  }

  const success_status_code: number[] = [
    ...(success2xxResponse?.statusCode || []),
    ...(success202Response?.statusCode || []),
    ...(success204Response?.statusCode || []),
  ];
  const lro_base_status_code = success_status_code.filter((code) => [200, 201].includes(code));
  if (lro_base_status_code.length === 0 && lroMetadata !== undefined && operation.verb === "delete") {
    const lro_response: CMDHttpResponse = {
      statusCode: [200, 201],
      isError: false,
      description: "Response schema for long-running operation.",
    };
    responses.push(lro_response);
  }

  if (redirectResponse !== undefined) {
    responses.push(redirectResponse);
  }
  responses.push(...errorResponses);

  if (lroMetadata !== undefined && lroMetadata.logicalResult) {
    // TODO: add logicalResult in responses
  }

  return responses;
}

function convert2CMDHttpResponse(
  context: AAZOperationEmitterContext,
  response: HttpOperationResponse,
  statusCodes: string[] | undefined,
  isError: boolean,
): CMDHttpResponse {
  const res: CMDHttpResponse = {
    statusCode: statusCodes?.map((code) => Number(code)),
    isError: isError ? true : undefined,
    description: response.description ?? getResponseDescriptionForStatusCodes(statusCodes),
  };

  const contentTypes: string[] = [];
  let body: HttpPayloadBody | undefined;
  for (const data of response.responses) {
    if (data.headers && Object.keys(data.headers).length > 0) {
      res.header ??= {
        items: [],
      };
      for (const name of Object.keys(data.headers)) {
        res.header.items.push({ name });
      }
    }
    if (data.body) {
      if (body && body.type !== data.body.type) {
        reportDiagnostic(context.program, {
          code: "duplicate-body-types",
          target: response.type,
        });
      }
      body = data.body;
      contentTypes.push(...data.body.contentTypes);
    }
  }
  if (body) {
    const isBinary = contentTypes.every((t) => isBinaryPayload(body!.type, t));
    if (isBinary) {
      throw new Error("NotImplementedError: Binary response are not supported.");
    }
    if (body.bodyKind === "multipart") {
      throw new Error("NotImplementedError: Multipart form data responses are not supported.");
    }
    let schema;
    if (isError) {
      const errorFormat = classifyErrorFormat(context, body.type);
      if (errorFormat === undefined) {
        throw new Error("Error response schema is not supported yet.");
      }
      schema = {
        readOnly: true,
        type: `@${errorFormat}`,
      };
    } else {
      schema = convert2CMDSchemaBase(
        {
          ...context,
          supportClsSchema: true,
          visibility: Visibility.Read,
        },
        body.type,
      );
    }
    if (!schema) {
      throw new Error("Invalid Response Schema. It's None.");
    }

    res.body = {
      json: {
        schema: schema,
      },
    };
  }
  return res;
}

// Schema functions

function getCollectionFormat(
  context: AAZOperationEmitterContext,
  type: ModelProperty,
  explode?: boolean,
): "csv" | "ssv" | "pipes" | "multi" | undefined {
  if (explode) {
    return "multi";
  }
  const encode = getEncode(context.program, type);
  if (encode) {
    if (encode?.encoding === "ArrayEncoding.pipeDelimited") {
      return "pipes";
    }
    if (encode?.encoding === "ArrayEncoding.spaceDelimited") {
      return "ssv";
    }
  }
  return "csv";
}

function buildSchemaEmitterContext(
  context: AAZOperationEmitterContext,
  httpProperty: HttpProperty,
): AAZSchemaEmitterContext {
  let collectionFormat;
  if (httpProperty.kind === "query") {
    collectionFormat = getCollectionFormat(context, httpProperty.property, httpProperty.options.explode);
  } else if (httpProperty.kind === "header") {
    const headerOptions = getHeaderFieldOptions(context.program, httpProperty.property);
    collectionFormat = getCollectionFormat(context, httpProperty.property, headerOptions.explode);
  }
  if (collectionFormat === "csv") {
    collectionFormat = undefined;
  }
  return {
    ...context,
    collectionFormat,
    supportClsSchema: true,
  };
}

function convert2CMDSchema(
  context: AAZSchemaEmitterContext,
  param: ModelProperty,
  name?: string,
): CMDSchema | undefined {
  if (isNeverType(param.type)) {
    return undefined;
  }
  let schema;
  switch (param.type.kind) {
    case "Intrinsic":
      schema = convert2CMDSchemaBase(context, param.type);
      break;
    case "Model":
      schema = convert2CMDSchemaBase(context, param.type as Model);
      break;
    case "ModelProperty":
      schema = convert2CMDSchema(context, param.type as ModelProperty);
      break;
    case "Scalar":
      schema = convert2CMDSchemaBase(context, param.type as Scalar);
      break;
    case "UnionVariant":
      schema = convert2CMDSchemaBase(context, param.type.type);
      break;
    case "Union":
      schema = convert2CMDSchemaBase(context, param.type as Union);
      break;
    case "Enum":
      schema = convert2CMDSchemaBase(context, param.type as Enum);
      break;
    // TODO: handle Literals
    case "Number":
    case "String":
    case "Boolean":
      schema = convert2CMDSchemaBase(context, param.type);
      break;
    // case "Tuple":
    default:
      reportDiagnostic(context.program, { code: "Unsupported-Type", target: param.type });
  }
  if (schema) {
    schema = {
      ...schema,
      name: name ?? param.name,
      description: getDoc(context.program, param),
    };

    if (param.defaultValue) {
      schema.default = {
        value: getDefaultValue(context, param.defaultValue, param),
      };
    }
  }
  if (schema) {
    schema = {
      ...schema,
      ...applySchemaFormat(context, param, schema as CMDSchemaBase),
    };
    schema = {
      ...schema,
      ...applyEncoding(context, param, schema),
    };
    schema = {
      ...schema,
      ...applyExtensionsDecorators(context, param, schema),
    };
  }
  return schema;
}

function convert2CMDSchemaBase(context: AAZSchemaEmitterContext, type: Type): CMDSchemaBase | undefined {
  if (isNeverType(type)) {
    return undefined;
  }
  let schema;
  switch (type.kind) {
    case "Intrinsic":
      schema = convertIntrinsic2CMDSchemaBase(context, type);
      break;
    case "Scalar":
      schema = convertScalar2CMDSchemaBase(context, type as Scalar);
      break;
    case "Model":
      if (isArrayModelType(context.program, type)) {
        schema = convertModel2CMDArraySchemaBase(context, type as Model);
      } else {
        schema = convertModel2CMDObjectSchemaBase(context, type as Model);
      }
      break;
    case "ModelProperty":
      schema = convert2CMDSchema(context, type.type as ModelProperty);
      break;
    case "UnionVariant":
      schema = convert2CMDSchemaBase(context, type.type);
      break;
    case "Union":
      schema = convertUnion2CMDSchemaBase(context, type as Union);
      break;
    case "Enum":
      schema = convertEnum2CMDSchemaBase(context, type as Enum);
      break;
    // TODO: handle Literals
    case "Number":
    case "String":
    case "Boolean":
      schema = convertLiteral2CMDSchemaBase(context, type);
      break;
    // case "Tuple":
    default:
      reportDiagnostic(context.program, { code: "Unsupported-Type", target: type });
  }
  if (schema) {
    schema = applySchemaFormat(context, type, schema);
    schema = applyEncoding(context, type, schema);
    schema = applyExtensionsDecorators(context, type, schema);
  }

  return schema;
}

function convertModel2CMDObjectSchemaBase(
  context: AAZSchemaEmitterContext,
  model: Model,
): CMDObjectSchemaBase | CMDClsSchemaBase | undefined {
  const payloadModel = context.metadateInfo.getEffectivePayloadType(model, context.visibility) as Model;
  if (isArrayModelType(context.program, payloadModel)) {
    return undefined;
  }

  let pending;
  if (context.supportClsSchema) {
    pending = context.pendingSchemas.getOrAdd(payloadModel, context.visibility, () => ({
      type: payloadModel,
      visibility: context.visibility,
      ref: context.refs.getOrAdd(payloadModel, context.visibility, () => new Ref()),
      count: 0,
    }));
    pending.count++;
    if (pending.count > 1) {
      return {
        type: new ClsType(pending),
      } as CMDClsSchemaBase;
    }
  }

  // const name = getOpenAPITypeName(context.program, type, context.typeNameOptions);

  let object: CMDObjectSchemaBase = {
    type: "object",
    cls: pending?.ref,
  };

  const properties: Record<string, CMDSchema> = {};

  // inherit from base model
  if (payloadModel.baseModel) {
    const baseSchema = convert2CMDSchemaBase(
      {
        ...context,
        supportClsSchema: false,
      },
      payloadModel.baseModel,
    );
    if (baseSchema) {
      Object.assign(object, baseSchema, { cls: pending?.ref });
    }
    const discriminatorInfo = getDiscriminatorInfo(context, payloadModel);
    if (discriminatorInfo) {
      // directly use child definition instead of polymorphism.
      // So the value for discriminator property is const.
      // filter prop in object.props by discriminatorInfo.propertyName and set its const value
      const prop = object.props!.find((prop) => prop.name === discriminatorInfo.propertyName)!;
      prop.const = true;
      prop.default = {
        value: discriminatorInfo.value,
      };
      object.discriminators = undefined;
    }

    if (object.props) {
      for (const prop of object.props) {
        properties[prop.name] = prop;
      }
      object.props = undefined;
    }
  }

  const discriminator = getDiscriminator(context.program, payloadModel);

  for (const prop of payloadModel.properties.values()) {
    if (isNeverType(prop.type)) {
      // If the property has a type of 'never', don't include it in the schema
      continue;
    }
    if (!context.metadateInfo.isPayloadProperty(prop, context.visibility)) {
      continue;
    }

    const jsonName = getJsonName(context, prop);
    let schema = convert2CMDSchema(
      {
        ...context,
        supportClsSchema: true,
      },
      prop,
      jsonName,
    );
    if (schema) {
      if (!context.metadateInfo.isOptional(prop, context.visibility) || prop.name === discriminator?.propertyName) {
        schema.required = true;
      }
      if (isReadonlyProperty(context.program, prop)) {
        schema.readOnly = true;
        if (schema.required) {
          // read_only property is not required
          // console.log("Ignore requirement of the read only property: ", schema.name)
          schema.required = false;
        }
      }
      if (shouldClientFlatten(context, prop)) {
        if (schema.type === "object") {
          schema = {
            ...schema,
            clientFlatten: true,
          } as CMDObjectSchema;
        } else if (schema.type instanceof ClsType) {
          schema = {
            ...schema,
            clientFlatten: true,
          } as CMDClsSchema;
        }
      }
      properties[schema.name] = schema;
    }
  }

  if (discriminator) {
    const { propertyName } = discriminator;
    console.assert(object.discriminators === undefined, "Discriminator should be undefined.");
    // Push discriminator into base type, but only if it is not already there
    if (!payloadModel.properties.get(propertyName)) {
      const discriminatorProperty: CMDStringSchema = {
        name: propertyName,
        type: "string",
        required: true,
        description: `Discriminator property for ${payloadModel.name}.`,
      };
      properties[propertyName] = discriminatorProperty;
    }

    const derivedModels = payloadModel.derivedModels.filter(includeDerivedModel);
    for (const child of derivedModels) {
      const childDiscriminatorValue = getDiscriminatorInfo(context, child);
      if (childDiscriminatorValue) {
        const disc = convertModel2CMDObjectDiscriminator(context, child, childDiscriminatorValue);
        if (disc) {
          object.discriminators ??= [];
          object.discriminators.push(disc);
        }
      }
    }
  }

  if (isRecordModelType(context.program, payloadModel)) {
    object.additionalProps = {
      item: convert2CMDSchemaBase(
        {
          ...context,
          supportClsSchema: true,
        },
        payloadModel.indexer.value,
      ),
    };
  }

  if (isAzureResourceOverall(context, payloadModel) && properties.location) {
    properties.location = {
      ...(properties.location as CMDStringSchema),
      type: "ResourceLocation",
    } as CMDResourceLocationSchema;
  }

  if (properties.userAssignedIdentities && properties.type) {
    object = {
      ...object,
      type: "IdentityObject",
    } as CMDIdentityObjectSchemaBase;
  }

  if (Object.keys(properties).length > 0) {
    object.props = Object.values(properties).filter((prop) => !isEmptiedSchema(prop));
    if (object.props.length === 0) {
      object.props = undefined;
    }
  }

  if (pending) {
    pending.schema = object;
  }

  return object;
}

function convertModel2CMDArraySchemaBase(
  context: AAZSchemaEmitterContext,
  model: Model,
): CMDArraySchemaBase | CMDClsSchemaBase | undefined {
  const payloadModel = context.metadateInfo.getEffectivePayloadType(model, context.visibility) as Model;
  if (!isArrayModelType(context.program, payloadModel)) {
    return undefined;
  }

  const item = convert2CMDSchemaBase(
    {
      ...context,
      supportClsSchema: true,
    },
    payloadModel.indexer.value!,
  );
  if (!item) {
    return undefined;
  }
  const array: CMDArraySchemaBase = {
    type: new ArrayType(item.type),
    item: item,
    identifiers: getExtensions(context.program, payloadModel).get("x-ms-identifiers"),
  };
  return array;
}

function convertModel2CMDObjectDiscriminator(
  context: AAZSchemaEmitterContext,
  model: Model,
  discriminatorInfo: DiscriminatorInfo,
): CMDObjectSchemaDiscriminator | undefined {
  const object: CMDObjectSchemaDiscriminator = {
    property: discriminatorInfo.propertyName,
    value: discriminatorInfo.value,
  };

  const payloadModel = context.metadateInfo.getEffectivePayloadType(model, context.visibility) as Model;

  const properties: Record<string, CMDSchema> = {};
  const discriminator = getDiscriminator(context.program, payloadModel);

  for (const prop of payloadModel.properties.values()) {
    if (isNeverType(prop.type)) {
      // If the property has a type of 'never', don't include it in the schema
      continue;
    }
    if (!context.metadateInfo.isPayloadProperty(prop, context.visibility)) {
      continue;
    }

    const jsonName = getJsonName(context, prop);
    if (jsonName === discriminatorInfo.propertyName) {
      // if this property is a discriminator property, remove it as autorest
      continue;
    }
    let schema = convert2CMDSchema(
      {
        ...context,
        supportClsSchema: true,
      },
      prop,
      jsonName,
    );

    if (schema) {
      if (isReadonlyProperty(context.program, prop)) {
        schema.readOnly = true;
      }
      if (!context.metadateInfo.isOptional(prop, context.visibility) || prop.name === discriminator?.propertyName) {
        schema.required = true;
      }
      if (shouldClientFlatten(context, prop)) {
        if (schema.type === "object") {
          schema = {
            ...schema,
            clientFlatten: true,
          } as CMDObjectSchema;
        } else if (schema.type instanceof ClsType) {
          schema = {
            ...schema,
            clientFlatten: true,
          } as CMDClsSchema;
        }
      }
      properties[schema.name] = schema;
    }
  }

  // TODO: handle discriminator.propertyName === discriminatorInfo.propertyName
  if (discriminator && discriminator.propertyName !== discriminatorInfo.propertyName) {
    const { propertyName } = discriminator;
    console.assert(object.discriminators === undefined, "Discriminator should be undefined.");
    // Push discriminator into base type, but only if it is not already there
    if (!payloadModel.properties.get(propertyName)) {
      const discriminatorProperty: CMDStringSchema = {
        name: propertyName,
        type: "string",
        required: true,
        description: `Discriminator property for ${payloadModel.name}.`,
      };
      properties[propertyName] = discriminatorProperty;
    }

    const discProperty = properties[propertyName] as CMDStringSchema;

    const derivedModels = payloadModel.derivedModels.filter(includeDerivedModel);
    for (const child of derivedModels) {
      const childDiscriminatorValue = getDiscriminatorInfo(context, child);
      if (childDiscriminatorValue) {
        const disc = convertModel2CMDObjectDiscriminator(context, child, childDiscriminatorValue);
        if (disc) {
          object.discriminators ??= [];
          object.discriminators.push(disc);
          discProperty.enum ??= {
            items: [],
          };
          discProperty.enum.items.push({
            value: childDiscriminatorValue.value,
          });
        }
      }
    }
  }

  if (Object.keys(properties).length > 0) {
    object.props = Object.values(properties).filter((prop) => !isEmptiedSchema(prop));
    if (object.props.length === 0) {
      object.props = undefined;
    }
  }

  return object;
}

function convertScalar2CMDSchemaBase(context: AAZSchemaEmitterContext, scalar: Scalar): CMDSchemaBase | undefined {
  const isStd = context.program.checker.isStdType(scalar);
  const encodeData = getEncode(context.program, scalar);
  let schema;
  if (isStd) {
    switch (scalar.name) {
      case "bytes":
        schema = {
          type: "byte",
        } as CMDByteSchemaBase;
        break;
      case "numeric":
        schema = {
          type: "integer",
        } as CMDIntegerSchemaBase;
        break;
      case "integer":
        schema = {
          type: "integer",
        } as CMDIntegerSchemaBase;
        break;
      case "int8":
        // TODO: add format for int8
        schema = {
          type: "integer",
        } as CMDIntegerSchemaBase;
        break;
      case "int16":
        // TODO: add format for int16
        schema = {
          type: "integer",
        } as CMDIntegerSchemaBase;
        break;
      case "int32":
        schema = {
          type: "integer32",
        } as CMDInteger32SchemaBase;
        break;
      case "int64":
        schema = {
          type: "integer64",
        } as CMDInteger64SchemaBase;
        break;
      case "safeint":
        schema = {
          type: "integer64",
        } as CMDInteger64SchemaBase;
        break;
      case "uint8":
        // TODO: add format for uint8
        schema = {
          type: "integer",
        } as CMDIntegerSchemaBase;
        break;
      case "uint16":
        // TODO: add format for uint16
        schema = {
          type: "integer",
        } as CMDIntegerSchemaBase;
        break;
      case "uint32":
        // TODO: add format for uint32
        schema = {
          type: "integer",
        } as CMDIntegerSchemaBase;
        break;
      case "uint64":
        // TODO: add format for uint64
        schema = {
          type: "integer",
        } as CMDIntegerSchemaBase;
        break;
      case "float":
        schema = {
          type: "float",
        } as CMDFloatSchemaBase;
        break;
      case "float32":
        schema = {
          type: "float32",
        } as CMDFloat32SchemaBase;
        break;
      case "float64":
        schema = {
          type: "float64",
        } as CMDFloat64SchemaBase;
        break;
      case "decimal":
        schema = {
          type: "float64",
        } as CMDFloat64SchemaBase;
        break;
      case "decimal128":
        // TODO: add format for decimal128
        schema = {
          type: "float",
        } as CMDFloatSchemaBase;
        break;
      case "string":
        schema = {
          type: "string",
        } as CMDStringSchemaBase;
        break;
      case "url":
        schema = {
          type: "string",
        } as CMDStringSchemaBase;
        break;
      case "plainDate":
        schema = {
          type: "date",
        };
        break;
      case "plainTime":
        schema = {
          type: "time",
        };
        break;
      case "utcDateTime":
      case "offsetDateTime":
        switch (encodeData?.encoding) {
          case "rfc3339":
            schema = { type: "dateTime" };
            break;
          case "unixTimestamp":
            // TODO: add "unixtime" support
            schema = { type: "dateTime" };
            break;
          case "rfc7231":
            // TODO: add "date-time-rfc7231" support
            schema = { type: "dateTime" };
            break;
          default:
            if (encodeData !== undefined) {
              schema = convertScalar2CMDSchemaBase(context, encodeData.type);
            }
            schema ??= { type: "dateTime" };
        }
        break;
      case "duration":
        switch (encodeData?.encoding) {
          case "ISO8601":
            schema = { type: "duration" };
            break;
          case "seconds":
            // TODO: add "seconds" support
            schema = { type: "duration" };
            break;
          default:
            if (encodeData !== undefined) {
              schema = convertScalar2CMDSchemaBase(context, encodeData.type);
            }
            schema ??= { type: "duration" };
        }
        break;
      case "boolean":
        schema = { type: "boolean" };
        break;
    }
  } else if (scalar.baseScalar) {
    schema = convertScalar2CMDSchemaBase(context, scalar.baseScalar);
  }

  return schema;
}

function convertUnion2CMDSchemaBase(context: AAZSchemaEmitterContext, union: Union): CMDSchemaBase | undefined {
  const nonNullOptions = [...union.variants.values()].map((x) => x.type).filter((t) => !isNullType(t));
  const nullable = union.variants.size !== nonNullOptions.length;
  if (nonNullOptions.length === 0) {
    reportDiagnostic(context.program, { code: "union-null", target: union });
    return undefined;
  }

  let schema;
  if (nonNullOptions.length === 1) {
    const type = nonNullOptions[0];
    schema = {
      ...convert2CMDSchemaBase(context, type)!,
      nullable: nullable ? true : undefined,
    };
  } else {
    const [asEnum] = getUnionAsEnum(union);
    if (asEnum) {
      schema = convertUnionEnum2CMDSchemaBase(context, union, asEnum);
    } else {
      reportDiagnostic(context.program, {
        code: "union-unsupported",
        target: union,
      });
    }
  }
  return schema;
}

function convertIntrinsic2CMDSchemaBase(
  context: AAZSchemaEmitterContext,
  type: IntrinsicType,
): CMDAnyTypeSchemaBase | undefined {
  let schema;
  if (type.name === "unknown") {
    schema = {
      type: "any",
    } as CMDAnyTypeSchemaBase;
  }
  return schema;
}

function convertUnionEnum2CMDSchemaBase(
  context: AAZSchemaEmitterContext,
  union: Union,
  e: UnionEnum,
): CMDStringSchemaBase | CMDIntegerSchemaBase | undefined {
  let schema;
  if (e.kind === "number") {
    schema = {
      type: "integer",
      nullable: e.nullable ? true : undefined,
      enum: {
        items: Array.from(e.flattenedMembers.values()).map((member) => {
          return {
            value: member.value,
          };
        }),
      },
    } as CMDIntegerSchemaBase;
  } else if (e.kind === "string") {
    schema = {
      type: "string",
      nullable: e.nullable ? true : undefined,
      enum: {
        items: Array.from(e.flattenedMembers.values()).map((member) => {
          return {
            value: member.value,
          };
        }),
      },
    } as CMDStringSchemaBase;
  }
  // TODO: handle e.open which supports additional enum values
  return schema;
}

function convertEnum2CMDSchemaBase(
  context: AAZSchemaEmitterContext,
  e: Enum,
): CMDStringSchemaBase | CMDIntegerSchemaBase | undefined {
  let schema;
  const firstMember = e.members.values().next().value;
  if (firstMember === undefined) {
    return undefined;
  }
  const type = getEnumMemberType(firstMember);
  for (const option of e.members.values()) {
    if (type !== getEnumMemberType(option)) {
      return undefined;
    }
  }
  if (type === "number") {
    schema = {
      type: "integer",
      enum: {
        items: Array.from(e.members.values()).map((member) => {
          return {
            value: member.value! as number,
          };
        }),
      },
    } as CMDIntegerSchemaBase;
  } else if (type === "string") {
    schema = {
      type: "string",
      enum: {
        items: Array.from(e.members.values()).map((member) => {
          return {
            value: (member.value ?? member.name) as string,
          };
        }),
      },
    } as CMDStringSchemaBase;
  }
  return schema;

  function getEnumMemberType(member: EnumMember): "string" | "number" {
    if (typeof member.value === "number") {
      return "number";
    }
    return "string";
  }
}

function shouldClientFlatten(context: AAZSchemaEmitterContext, target: ModelProperty): boolean {
  return !!(
    shouldFlattenProperty(context.tcgcContext, target) ||
    getExtensions(context.program, target).get("x-ms-client-flatten")
  );
}

function includeDerivedModel(model: Model): boolean {
  return (
    !isTemplateDeclaration(model) &&
    (model.templateMapper?.args === undefined ||
      model.templateMapper?.args.length === 0 ||
      model.derivedModels.length > 0)
  );
}

function getDiscriminatorInfo(context: AAZSchemaEmitterContext, model: Model): DiscriminatorInfo | undefined {
  let discriminator;
  let current = model;
  while (current.baseModel) {
    discriminator = getDiscriminator(context.program, current.baseModel);
    if (discriminator) {
      break;
    }
    current = current.baseModel;
  }
  if (discriminator === undefined) {
    return undefined;
  }
  const prop = getProperty(model, discriminator.propertyName);
  if (prop) {
    const values = getStringValues(prop.type);
    if (values.length === 1) {
      return { propertyName: discriminator.propertyName, value: values[0] };
    }
  }
  return undefined;
}

function isAzureResourceOverall(context: AAZSchemaEmitterContext, model: Model): boolean {
  let current = model;
  let isResource = isAzureResource(context.program, current);
  while (!isResource && current.baseModel) {
    current = current.baseModel;
    isResource = isAzureResource(context.program, current);
  }
  return !!isResource;
}

function convertLiteral2CMDSchemaBase(
  context: AAZSchemaEmitterContext,
  type: Type,
): CMDStringSchemaBase | CMDIntegerSchemaBase | CMDFloatSchemaBase | CMDBooleanSchemaBase | undefined {
  switch (type.kind) {
    case "Number":
      if (type.numericValue.isInteger) {
        return {
          type: "integer",
          enum: {
            items: [{ value: type.value }],
          },
        };
      } else {
        return {
          type: "float",
          enum: {
            items: [{ value: type.value }],
          },
        };
      }
    case "String":
      return {
        type: "string",
        enum: {
          items: [{ value: type.value }],
        },
      };
    case "Boolean":
      return {
        type: "boolean",
      };
    default:
      return undefined;
  }
}

// Return any string literal values for type
function getStringValues(type: Type): string[] {
  switch (type.kind) {
    case "String":
      return [type.value];
    case "Union":
      return [...type.variants.values()].flatMap((x) => getStringValues(x.type)).filter((x) => x);
    case "EnumMember":
      return typeof type.value !== "number" ? [type.value ?? type.name] : [];
    case "UnionVariant":
      return getStringValues(type.type);
    default:
      return [];
  }
}

function processPendingSchemas(
  context: AAZOperationEmitterContext,
  verbVisibility: Visibility,
  suffix: "read" | "create" | "update",
) {
  for (const type of context.pendingSchemas.keys()) {
    const group = context.pendingSchemas.get(type)!;
    for (const visibility of group.keys()) {
      const pending = context.pendingSchemas.get(type)!.get(visibility)!;
      if (pending.count < 2) {
        pending.ref!.value = undefined;
      } else {
        const name = getOpenAPITypeName(context.program, type, context.typeNameOptions);
        let ref_name = toCamelCase(name.replace(/\./g, " "));
        if (group.size > 1 && visibility !== Visibility.Read) {
          // TODO: handle item
          ref_name += getVisibilitySuffix(verbVisibility, Visibility.Read);
        }
        if (Visibility.Read !== visibility) {
          ref_name += "_" + suffix;
        } else {
          ref_name += "_read";
        }
        pending.ref!.value = ref_name;
      }
    }
  }
}

function isEmptiedSchema(schema: CMDSchema): boolean {
  if (!schema.required) {
    if (schema.type === "object") {
      const objectSchema = schema as CMDObjectSchema;
      if (
        !objectSchema.additionalProps &&
        !objectSchema.props &&
        !objectSchema.discriminators &&
        !objectSchema.nullable
      ) {
        return true;
      }
    } else if (schema.type instanceof ArrayType) {
      const arraySchema = schema as CMDArraySchemaBase;
      if (!arraySchema.item && !arraySchema.nullable) {
        return true;
      }
    }
  }
  return false;
}

// format functions
function applySchemaFormat(context: AAZSchemaEmitterContext, type: Type, target: CMDSchemaBase): CMDSchemaBase {
  let schema = target;
  const formatStr = getFormat(context.program, type);
  switch (target.type) {
    case "byte":
      schema = {
        ...schema,
        format: emitStringFormat(context, type, (schema as CMDByteSchemaBase).format),
      } as CMDByteSchemaBase;
      break;
    case "integer":
      schema = {
        ...schema,
        format: emitIntegerFormat(context, type, (schema as CMDIntegerSchemaBase).format),
      } as CMDIntegerSchemaBase;
      break;
    case "integer32":
      schema = {
        ...schema,
        format: emitIntegerFormat(context, type, (schema as CMDInteger32SchemaBase).format),
      } as CMDInteger32SchemaBase;
      break;
    case "integer64":
      schema = {
        ...schema,
        format: emitIntegerFormat(context, type, (schema as CMDInteger64SchemaBase).format),
      } as CMDInteger64SchemaBase;
      break;
    case "float":
      schema = {
        ...schema,
        format: emitFloatFormat(context, type, (schema as CMDFloatSchemaBase).format),
      } as CMDFloatSchemaBase;
      break;
    case "float32":
      schema = {
        ...schema,
        format: emitFloatFormat(context, type, (schema as CMDFloat32SchemaBase).format),
      } as CMDFloat32SchemaBase;
      break;
    case "float64":
      schema = {
        ...schema,
        format: emitFloatFormat(context, type, (schema as CMDFloat64SchemaBase).format),
      } as CMDFloat64SchemaBase;
      break;
    case "ResourceId":
      schema = {
        ...schema,
        type: "ResourceId",
        format: emitResourceIdFormat(context, type, (schema as CMDResourceIdSchemaBase).format),
      } as CMDResourceIdSchemaBase;
      break;
    case "string":
      switch (formatStr) {
        case "uuid":
          schema = {
            ...schema,
            type: "uuid",
            format: emitStringFormat(context, type, (schema as CMDStringSchemaBase).format),
          } as CMDUuidSchemaBase;
          break;
        case "password":
          schema = {
            ...schema,
            type: "password",
            format: emitStringFormat(context, type, (schema as CMDStringSchemaBase).format),
          } as CMDPasswordSchemaBase;
          break;
        // TODO: add certificate supports
        case "arm-id":
          schema = {
            ...schema,
            type: "ResourceId",
            format: emitResourceIdFormat(context, type, undefined),
          } as CMDResourceIdSchemaBase;
          break;
        case "date":
          schema = {
            ...schema,
            type: "date",
            format: emitStringFormat(context, type, (schema as CMDStringSchemaBase).format),
          } as CMDDateSchemaBase;
          break;
        case "date-time":
          schema = {
            ...schema,
            type: "date-time",
            format: emitStringFormat(context, type, (schema as CMDStringSchemaBase).format),
          } as CMDDateTimeSchemaBase;
          break;
        case "date-time-rfc1123":
          // TODO: add "date-time-rfc1123" support
          schema = {
            ...schema,
            type: "date-time",
            format: emitStringFormat(context, type, (schema as CMDStringSchemaBase).format),
          } as CMDDateTimeSchemaBase;
          break;
        case "date-time-rfc7231":
          // TODO: add "date-time-rfc7231" support
          schema = {
            ...schema,
            type: "date-time",
            format: emitStringFormat(context, type, (schema as CMDStringSchemaBase).format),
          } as CMDDateTimeSchemaBase;
          break;
        case "duration":
          schema = {
            ...schema,
            type: "duration",
            format: emitStringFormat(context, type, (schema as CMDStringSchemaBase).format),
          } as CMDDurationSchemaBase;
          break;
        default:
          schema = {
            ...schema,
            format: emitStringFormat(context, type, (schema as CMDStringSchemaBase).format),
          } as CMDStringSchemaBase;
      }
      break;
    case "uuid":
      schema = {
        ...schema,
        format: emitStringFormat(context, type, (schema as CMDStringSchemaBase).format),
      } as CMDUuidSchemaBase;
      break;
    // case "date":
    // case "time":
    // case "dateTime":
    // case "duration":
    // case "boolean":
    case "object":
      schema = {
        ...schema,
        format: emitObjectFormat(context, type as Model, (schema as CMDObjectSchemaBase).format),
      } as CMDObjectSchemaBase;
      break;
    default:
      if (schema.type instanceof ArrayType) {
        schema = {
          ...schema,
          format: emitArrayFormat(context, type as Model, (schema as CMDArraySchemaBase).format),
        } as CMDArraySchemaBase;
      }
  }
  return schema;
}

function emitStringFormat(
  context: AAZSchemaEmitterContext,
  type: Type,
  targetFormat: CMDStringFormat | undefined,
): CMDStringFormat | undefined {
  let format = targetFormat;

  const pattern = getPattern(context.program, type);
  if (pattern !== undefined) {
    format = {
      ...(format ?? {}),
      pattern,
    };
  }

  const maxLength = getMaxLength(context.program, type);
  if (maxLength !== undefined) {
    format = {
      ...(format ?? {}),
      maxLength,
    };
  }

  const minLength = getMinLength(context.program, type);
  if (minLength !== undefined) {
    format = {
      ...(format ?? {}),
      minLength,
    };
  }

  return format;
}

function emitResourceIdFormat(
  context: AAZSchemaEmitterContext,
  type: Type,
  targetFormat: CMDResourceIdFormat | undefined,
): CMDResourceIdFormat | undefined {
  // TODO:
  let format = targetFormat;
  const ext = getArmResourceIdentifierConfig(context.program, type as Scalar);
  if (ext && ext.allowedResources.length === 1) {
    const type = ext.allowedResources[0].type;
    const scopes = ext.allowedResources[0].scopes ?? ["ResourceGroup"];
    if (scopes.length === 1) {
      switch (scopes[0]) {
        case "ResourceGroup":
          format = {
            template: "/subscriptions/{}/resourceGroups/{}/providers/" + type + "/{}",
          };
          break;
        case "Subscription":
          format = {
            template: "/subscriptions/{}/providers/" + type + "/{}",
          };
          break;
        case "ManagementGroup":
          return {
            template: "/providers/Microsoft.Management/managementGroups/{}/providers/" + type + "/{}",
          };
        case "Extension":
        case "Tenant":
          break;
      }
    }
  }
  return format;
}

function emitIntegerFormat(
  context: AAZSchemaEmitterContext,
  type: Type,
  targetFormat: CMDIntegerFormat | undefined,
): CMDIntegerFormat | undefined {
  let format = targetFormat;

  const maximum = getMaxValue(context.program, type);
  if (maximum !== undefined) {
    format = {
      ...(format ?? {}),
      maximum,
    };
  }

  const minimum = getMinValue(context.program, type);
  if (minimum !== undefined) {
    format = {
      ...(format ?? {}),
      minimum,
    };
  }

  const multipleOf = getMultipleOf(context.program, type);
  if (multipleOf !== undefined) {
    format = {
      ...(format ?? {}),
      multipleOf,
    };
  }

  return format;
}

function emitFloatFormat(
  context: AAZSchemaEmitterContext,
  type: Type,
  targetFormat: CMDFloatFormat | undefined,
): CMDFloatFormat | undefined {
  let format = targetFormat;

  const maximum = getMaxValue(context.program, type);
  if (maximum !== undefined) {
    format = {
      ...(format ?? {}),
      maximum,
    };
  }

  const minimum = getMinValue(context.program, type);
  if (minimum !== undefined) {
    format = {
      ...(format ?? {}),
      minimum,
    };
  }

  const minValueExclusive = getMinValueExclusive(context.program, type);
  if (minValueExclusive !== undefined) {
    format = {
      ...(format ?? {}),
      minimum: minValueExclusive,
      exclusiveMinimum: true,
    };
  }

  const maxValueExclusive = getMaxValueExclusive(context.program, type);
  if (maxValueExclusive !== undefined) {
    format = {
      ...(format ?? {}),
      maximum: maxValueExclusive,
      exclusiveMaximum: true,
    };
  }

  const multipleOf = getMultipleOf(context.program, type);
  if (multipleOf !== undefined) {
    format = {
      ...(format ?? {}),
      multipleOf,
    };
  }

  return format;
}

function emitObjectFormat(
  context: AAZSchemaEmitterContext,
  type: Model,
  targetFormat: CMDObjectFormat | undefined,
): CMDObjectFormat | undefined {
  let format = targetFormat;

  const maxProperties = getMaxProperties(context.program, type);
  if (maxProperties !== undefined) {
    format = {
      ...(format ?? {}),
      maxProperties,
    };
  }

  const minProperties = getMinProperties(context.program, type);
  if (minProperties !== undefined) {
    format = {
      ...(format ?? {}),
      minProperties,
    };
  }

  return format;
}

function emitArrayFormat(
  context: AAZSchemaEmitterContext,
  type: Model,
  targetFormat: CMDArrayFormat | undefined,
): CMDArrayFormat | undefined {
  let format = targetFormat;

  const maxLength = getMaxItems(context.program, type);
  if (maxLength !== undefined) {
    format = {
      ...(format ?? {}),
      maxLength,
    };
  }

  const minLength = getMinItems(context.program, type);
  if (minLength !== undefined) {
    format = {
      ...(format ?? {}),
      minLength,
    };
  }

  const uniqueItems = getUniqueItems(context.program, type);
  if (uniqueItems !== undefined) {
    format = {
      ...(format ?? {}),
      unique: true,
    };
  }

  if (context.collectionFormat !== undefined) {
    format = {
      ...(format ?? {}),
      strFormat: context.collectionFormat,
    };
  }

  return format;
}

// TODO: add emitResourceIdFormat

function applyEncoding(context: AAZSchemaEmitterContext, type: Type, schema: CMDSchemaBase): CMDSchemaBase {
  if (type.kind !== "Scalar" && type.kind !== "ModelProperty") {
    return schema;
  }
  const encodeData = getEncode(context.program, type);
  if (encodeData !== undefined) {
    schema = {
      ...schema,
      ...convertScalar2CMDSchemaBase(context, encodeData.type),
    };
  }
  return schema;
}

// apply extension decorators
function applyExtensionsDecorators(context: AAZSchemaEmitterContext, type: Type, schema: CMDSchemaBase): CMDSchemaBase {
  const extensions = getExtensions(context.program, type);
  if (extensions.has("x-ms-identifiers") && schema.type instanceof ArrayType) {
    (schema as CMDArraySchemaBase).identifiers = extensions.get("x-ms-identifiers");
  }
  if (extensions.has("x-ms-secret")) {
    (schema as CMDSchema).secret = extensions.get("x-ms-secret");
  }
  return schema;
}
// Utils functions

function getJsonName(context: AAZOperationEmitterContext, type: Type & { name: string }): string {
  const encodedName = resolveEncodedName(context.program, type, "application/json");
  return encodedName === type.name ? type.name : encodedName;
}

function getPathWithoutQuery(path: string): string {
  // strip everything from the key including and after the ?
  return path.replace(/\/?\?.*/, "");
}

function extractPagedMetadata(program: Program, operation: HttpOperation): XmsPageable | undefined {
  // `getPagedResult`/`PagedResultMetadata` were removed from @azure-tools/typespec-azure-core;
  // pagination metadata now comes from the compiler's `getPagingOperation`.
  const [paging] = getPagingOperation(program, operation.operation);
  if (paging === undefined) {
    return undefined;
  }
  // x-ms-pageable can only model nextLink-style paging. Use the operation's real @nextLink
  // property name; when it pages by continuationToken (no @nextLink), leave nextLinkName empty
  // instead of fabricating "nextLink" — downstream treats an empty name as "no next link"
  // (see _command.py `if pageable.next_link_name`), so a fake name would emit a broken pager.
  const nextLinkPath = paging.output.nextLink?.path;
  const nextLinkName =
    nextLinkPath && nextLinkPath.length > 0 ? nextLinkPath[nextLinkPath.length - 1].name : "";
  return {
    nextLinkName,
  };
}

function getModelOrScalarTypeIfNullable(type: Type): Model | Scalar | undefined {
  if (type.kind === "Model" || type.kind === "Scalar") {
    return type;
  } else if (type.kind === "Union") {
    // Remove all `null` types and make sure there's a single model type
    const nonNulls = [...type.variants.values()].map((x) => x.type).filter((variant) => !isNullType(variant));
    if (nonNulls.every((t) => t.kind === "Model" || t.kind === "Scalar")) {
      return nonNulls.length === 1 ? (nonNulls[0] as Model) : undefined;
    }
  }
  return undefined;
}

function isBinaryPayload(body: Type, contentType: string | string[]) {
  const types = new Set(typeof contentType === "string" ? [contentType] : contentType);
  return body.kind === "Scalar" && body.name === "bytes" && !types.has("application/json") && !types.has("text/plain");
}

function getOpenAPI2StatusCodes(
  context: AAZOperationEmitterContext,
  statusCodes: HttpStatusCodesEntry,
  diagnosticTarget: DiagnosticTarget,
): string[] {
  if (statusCodes === "*") {
    return ["default"];
  } else if (typeof statusCodes === "number") {
    return [String(statusCodes)];
  } else {
    return rangeToOpenAPI(context, statusCodes, diagnosticTarget);
  }
}

function rangeToOpenAPI(
  context: AAZOperationEmitterContext,
  range: HttpStatusCodeRange,
  diagnosticTarget: DiagnosticTarget,
): string[] {
  const reportInvalid = () =>
    reportDiagnostic(context.program, {
      code: "unsupported-status-code-range",
      format: { start: String(range.start), end: String(range.end) },
      target: diagnosticTarget,
    });

  const codes: string[] = [];
  let start = range.start;
  let end = range.end;

  if (range.start < 100) {
    reportInvalid();
    start = 100;
    codes.push("default");
  } else if (range.end > 599) {
    reportInvalid();
    codes.push("default");
    end = 599;
  }
  const groups = [1, 2, 3, 4, 5];

  for (const group of groups) {
    if (start > end) {
      break;
    }
    const groupStart = group * 100;
    const groupEnd = groupStart + 99;
    if (start >= groupStart && start <= groupEnd) {
      codes.push(`${group}XX`);
      if (start !== groupStart || end < groupEnd) {
        reportInvalid();
      }
      start = groupStart + 100;
    }
  }
  return codes;
}

function getResponseDescriptionForStatusCodes(statusCodes: string[] | undefined) {
  if (!statusCodes || statusCodes.length === 0) {
    return undefined;
  }
  if (statusCodes.includes("default")) {
    return undefined;
  }
  return getStatusCodeDescription(statusCodes[0]) ?? undefined;
}

function classifyErrorFormat(
  context: AAZOperationEmitterContext,
  type: Type,
): "ODataV4Format" | "MgmtErrorFormat" | undefined {
  // In order to not effect the normal schema's cls reference count, create the new context
  let schema = convert2CMDSchemaBase(
    {
      ...context,
      pendingSchemas: new TwoLevelMap(),
      refs: new TwoLevelMap(),
      visibility: Visibility.Read,
      supportClsSchema: true,
    },
    type,
  );

  if (schema === undefined) {
    return undefined;
  }

  if (schema.type instanceof ClsType) {
    schema = getClsDefinitionModel(schema as CMDClsSchemaBase);
  }
  if (schema.type !== "object" || (schema as CMDObjectSchemaBase).props === undefined) {
    return undefined;
  }
  let errorSchema = schema as CMDObjectSchemaBase;
  const props: Record<string, CMDSchema> = {};
  for (const prop of errorSchema.props!) {
    props[prop.name] = prop;
  }
  if (props.error) {
    if (props.error.type instanceof ClsType) {
      errorSchema = getClsDefinitionModel(props.error as CMDClsSchemaBase) as CMDObjectSchemaBase;
    } else if (props.error.type !== "object") {
      return undefined;
    }
    errorSchema = props.error as CMDObjectSchemaBase;
  }

  const propKeys = new Set();
  for (const prop of errorSchema.props!) {
    propKeys.add(prop.name);
  }

  if (!(propKeys.has("code") && propKeys.has("message"))) {
    return undefined;
  }

  // difference update propKeys with ["code", "message", "target", "details", "innerError", "innererror"]
  for (const key of ["code", "message", "target", "details", "innerError", "innererror"]) {
    propKeys.delete(key);
  }

  if (propKeys.size === 0) {
    return "ODataV4Format";
  }
  if (propKeys.size === 1 && propKeys.has("additionalInfo")) {
    return "MgmtErrorFormat";
  }
  return undefined;
}

function getClsDefinitionModel(schema: CMDClsSchemaBase): CMDObjectSchemaBase | CMDArraySchemaBase {
  return schema.type.pendingSchema.schema!;
}

function getDefaultValue(context: AAZSchemaEmitterContext, defaultType: Value, modelProperty: ModelProperty): any {
  return serializeValueAsJson(context.program, defaultType, modelProperty);
}
