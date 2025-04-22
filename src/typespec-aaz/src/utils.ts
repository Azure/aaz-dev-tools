import { Program, Type, isGlobalNamespace, isService } from "@typespec/compiler";
import { HttpOperation, isSharedRoute } from "@typespec/http";
import { getOperationId } from "@typespec/openapi";
import { pascalCase } from "change-case";
import { AAZEmitterContext } from "./context.js";
import { getClientNameOverride } from "@azure-tools/typespec-client-generator-core";

function getPathWithoutQuery(path: string): string {
  // strip everything from the key including and after the ?
  return path.replace(/\/?\?.*/, "");
}

const URL_PARAMETER_PLACEHOLDER = "{}";

// export function swaggerResourcePathToResourceIdTemplate(path: string): string {
//     const pathParts = path.split("?", 2);
//     const urlParts = pathParts[0].split("/");
//     let idx = 1;
//     while (idx < urlParts.length) {
//         if (idx === 1 && /^\{[^{}]*\}$/.test(urlParts[idx])) {
//             // ignore to the parameter name in first part of url, such as `/{parameter}` or `/{parameter}/...`
//             // But the placeholder in first part like `/indexes('{indexname}')` will be processed
//             idx++;
//             continue;
//         }
//         urlParts[idx] = urlParts[idx].replace(/\{[^{}]*\}/g, URL_PARAMETER_PLACEHOLDER);
//         idx++;
//     }
//     pathParts[0] = urlParts.join("/");
//     return pathParts.join("?");
// }

export function swaggerResourcePathToResourceId(path: string): string {
  const pathParts = path.split("?", 2);
  const urlParts = pathParts[0].split("/");
  let idx = 1;
  while (idx < urlParts.length) {
    if (idx === 1 && /^\{[^{}]*\}$/.test(urlParts[idx])) {
      idx++;
      continue;
    }
    urlParts[idx] = urlParts[idx].replace(/\{[^{}]*\}/g, URL_PARAMETER_PLACEHOLDER);
    idx++;
  }
  pathParts[0] = urlParts.join("/").toLowerCase();
  return pathParts.join("?");
}

export function getResourcePath(program: Program, operation: HttpOperation) {
  const { operation: op } = operation;
  let { path: fullPath } = operation;
  if (!isSharedRoute(program, op)) {
    fullPath = getPathWithoutQuery(fullPath);
  }
  return fullPath;
}

function getAutorestClientName(context: AAZEmitterContext, type: Type & { name: string }) {
  const clientName = getClientNameOverride(context.tcgcContext, type);
  return clientName ?? type.name;
}

/**
 * Resolve the OpenAPI operation ID for the given operation using the following logic:
 * - If @operationId was specified use that value
 * - If operation is defined at the root or under the service namespace return `<operation.name>`
 * - Otherwise(operation is under another namespace or interface) return `<namespace/interface.name>_<operation.name>`
 *
 * @param program TypeSpec Program
 * @param operation Operation
 * @returns Operation ID in this format `<name>` or `<group>_<name>`
 */
export function resolveOperationId(context: AAZEmitterContext, operation: HttpOperation) {
  const { operation: op } = operation;
  const explicitOperationId = getOperationId(context.program, op);
  if (explicitOperationId) {
    return explicitOperationId;
  }

  const operationName = getAutorestClientName(context, op);
  if (op.interface) {
    return pascalCaseForOperationId(`${getAutorestClientName(context, op.interface)}_${operationName}`);
  }
  const namespace = op.namespace;
  if (
    namespace === undefined ||
    isGlobalNamespace(context.program, namespace) ||
    isService(context.program, namespace)
  ) {
    return pascalCase(operationName);
  }

  return pascalCaseForOperationId(`${namespace.name}_${operationName}`);
}

// export function getResourceID(program: Program, operation: HttpOperation): string {
//     const { operation: op } = operation;
//     let { path: fullPath } = operation;
//     if (!isSharedRoute(program, op)) {
//         fullPath = getPathWithoutQuery(fullPath);
//     }
//     return swaggerResourcePathToResourceId(fullPath);
// }

function pascalCaseForOperationId(name: string) {
  return name
    .split("_")
    .map((s) => pascalCase(s))
    .join("_");
}

export function toCamelCase(name: string, delimiters: string = ""): string {
  const parts = name.replace(/[-_]/g, " ").split(" ");
  const camelCasedParts = parts.map((part) => {
    if (part) {
      return part.charAt(0).toUpperCase() + part.slice(1).toLowerCase();
    }
    return "";
  });
  return camelCasedParts.join(delimiters);
}
