import { JSONSchemaType, createTypeSpecLibrary } from "@typespec/compiler";

export interface AAZEmitterOptions {
  "operation": "list-resources" | "get-resources-operations";
  "api-version"?: string;
  "resources"?: string[];
}

const EmitterOptionsSchema: JSONSchemaType<AAZEmitterOptions> = {
  type: "object",
  additionalProperties: true,
  properties: {
    operation: {
      type: "string",
      enum: ["list-resources", "get-resources-operations"],
    },
    "api-version": {
      type: "string",
      nullable: true,
    },
    resources: {
      type: "array",
      items: {
        type: "string",
      },
      nullable: true,
    },
  },
  required: ["operation"],
}

const libDef = {
  name: "@azure-tools/typespec-aaz",
  diagnostics: {
    "Duplicated-success-202": {
      severity: "error",
      messages: {
        default: "Duplicated 202 responses",
      }
    },
    "Duplicated-success-204": {
      severity: "error",
      messages: {
        default: "Duplicated 202 responses",
      }
    },
    "Duplicated-redirect": {
      severity: "error",
      messages: {
        default: "Duplicated redirect responses",
      }
    },
    "missing-status-codes": {
      severity: "error",
      messages: {
        default: "Missing status codes",
      }
    },
    "invalid-program-versions": {
      severity: "error",
      messages: {
        default: "Invalid service versions from program",
      }
    },
    "duplicate-body-types": {
      severity: "error",
      messages: {
        default: "Duplicate body types",
      }
    },
    "Unsupported-Type": {
      severity: "error",
      messages: {
        default: "Unsupported type",
      }
    },
    "union-null": {
      severity: "error",
      messages: {
        default: "Union with null",
      }
    },
    "union-unsupported": {
      severity: "error",
      messages: {
        default: "Union with unsupported type",
      }
    },
    "unsupported-status-code-range": {
      severity: "error",
      messages: {
        default: "Unsupported status code range",
      }
    },
    "invalid-default": {
      severity: "error",
      messages: {
        default: "Invalid default value",
      }
    },
    "missing-host-parameter": {
      severity: "error",
      messages: {
        default: "Missing host parameter",
      }
    }
  },
  emitter: {
    options: EmitterOptionsSchema as JSONSchemaType<AAZEmitterOptions>,
  }
} as const;

export const $lib = createTypeSpecLibrary(libDef);
export const { reportDiagnostic, createStateSymbol, getTracer } = $lib;
